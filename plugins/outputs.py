
import matplotlib
try:
    matplotlib.use('TkAgg')
except Exception:
    pass
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import queue as queue_module


def _queue_color(size, maxsize):
    if maxsize == 0:
        return '#2ecc71'
    pct = size / maxsize
    if pct < 0.5:
        return '#2ecc71'
    if pct < 0.8:
        return '#f39c12'
    return '#e74c3c'


# observer - subscribes to telemetry subject and drives the live display
class RealTimeDashboard:

    def __init__(self, processed_queue, cfg, total_input_rows=0):
        self.processed_queue = processed_queue
        self.cfg = cfg
        self.done = False
        self.total_input_rows = total_input_rows

        self.x_vals = []
        self.y_vals = []
        self.y_avg  = []

        self.passed = 0

        # updated each frame via update() called by telemetry
        self.raw_size      = 0
        self.verified_size = 0
        self.proc_size     = 0
        self.max_size      = 1

    def update(self, raw_size, verified_size, proc_size, max_size):
        self.raw_size      = raw_size
        self.verified_size = verified_size
        self.proc_size     = proc_size
        self.max_size      = max_size

    def run(self, telemetry):
        charts  = self.cfg['visualizations']['data_charts']
        tel_cfg = self.cfg['visualizations']['telemetry']

        show_raw  = tel_cfg.get('show_raw_stream',          True)
        show_int  = tel_cfg.get('show_intermediate_stream', True)
        show_proc = tel_cfg.get('show_processed_stream',    True)

        n_rows = 1 + len(charts)
        fig, axes = plt.subplots(n_rows, 1, figsize=(11, 4 * n_rows))
        fig.patch.set_facecolor('#1a1a2e')

        if n_rows == 1:
            axes = [axes]

        for ax in axes:
            ax.set_facecolor('#16213e')
            ax.tick_params(colors='white')
            ax.xaxis.label.set_color('white')
            ax.yaxis.label.set_color('white')
            ax.title.set_color('white')
            for spine in ax.spines.values():
                spine.set_edgecolor('#444')

        ax_tel     = axes[0]
        chart_axes = axes[1:]

        # static setup for each chart axis - done once, never repeated in animate()
        # safe because we no longer call ax.clear() on these axes
        chart_lines = []
        chart_titles = []
        for i, chart_cfg in enumerate(charts):
            ax = chart_axes[i]
            ax.set_facecolor('#16213e')
            ax.set_xlabel(chart_cfg['x_axis'], color='white', fontsize=8)
            ax.set_ylabel(chart_cfg['y_axis'], color='white', fontsize=8)
            ax.tick_params(colors='white')
            for spine in ax.spines.values():
                spine.set_edgecolor('#444')

            if chart_cfg['type'] == 'real_time_line_graph_values':
                line, = ax.plot([], [], color='#3498db', linewidth=1.2)
            elif chart_cfg['type'] == 'real_time_line_graph_average':
                line, = ax.plot([], [], color='#e67e22', linewidth=1.8)
            else:
                line, = ax.plot([], [], color='#ffffff', linewidth=1.2)

            chart_lines.append(line)
            chart_titles.append(chart_cfg['title'])

        def animate(frame):
            telemetry.poll()

            # drain processed queue without blocking
            while True:
                try:
                    packet = self.processed_queue.get_nowait()
                    if packet is None:
                        self.done = True
                        continue
                    x_key = charts[0]['x_axis'] if charts else 'time_period'
                    self.x_vals.append(packet.get(x_key, len(self.x_vals)))
                    self.y_vals.append(packet.get('metric_value', 0))
                    self.y_avg.append(packet.get('computed_metric', 0))
                    self.passed += 1
                except queue_module.Empty:
                    break

            dropped = self.total_input_rows - self.passed
            status  = 'done' if self.done else 'running'
            fig.suptitle(
                f'real-time pipeline dashboard  |  '
                f'verified: {self.passed}   dropped: {dropped}   total: {self.total_input_rows}   [{status}]',
                fontsize=10, fontweight='bold', color='white'
            )

            # telemetry bars - still needs clear() since bar geometry changes every frame
            ax_tel.clear()
            ax_tel.set_facecolor('#16213e')
            ax_tel.set_title('queue telemetry  (green=ok  yellow=filling  red=backpressure)',
                             color='white', fontsize=9)
            ax_tel.set_xlim(0, 1)
            ax_tel.set_ylim(-0.3, 2.8)
            ax_tel.axis('off')

            all_bars = [
                ('raw queue',       self.raw_size,       show_raw,  2.2),
                ('verified queue',  self.verified_size,  show_int,  1.3),
                ('processed queue', self.proc_size,      show_proc, 0.4),
            ]
            bars = [(label, size, self.max_size, y) for label, size, flag, y in all_bars if flag]

            for label, size, maxsize, y in bars:
                pct = size / maxsize if maxsize > 0 else 0
                col = _queue_color(size, maxsize)
                ax_tel.barh(y, 1.0, color='#2a2a4a', height=0.5, left=0, zorder=0)
                ax_tel.barh(y, pct, color=col,       height=0.5, left=0, zorder=1)
                ax_tel.text(-0.01, y, f'{label}  {size}/{maxsize}',
                            ha='right', va='center', color='white', fontsize=8)

            # update each chart line in-place - no clear(), no re-plot, no static re-setup
            for i, chart_cfg in enumerate(charts):
                ax   = chart_axes[i]
                line = chart_lines[i]

                if not self.x_vals:
                    continue

                if chart_cfg['type'] == 'real_time_line_graph_values':
                    line.set_data(self.x_vals, self.y_vals)
                elif chart_cfg['type'] == 'real_time_line_graph_average':
                    line.set_data(self.x_vals, self.y_avg)

                ax.relim()
                ax.autoscale_view()

                # only thing that changes on the title is the [done] suffix and color
                title = chart_titles[i] + ('  [done]' if self.done else '')
                ax.set_title(title, color='#2ecc71' if self.done else 'white', fontsize=10)

            plt.tight_layout()

        ani = animation.FuncAnimation(fig, animate, interval=150, cache_frame_data=False)
        plt.show()
