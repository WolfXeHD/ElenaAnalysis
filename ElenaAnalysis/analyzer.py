from ElenaAnalysis import data_loading
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from calendar import monthrange
import matplotlib.dates as mdates
from dateutil.relativedelta import relativedelta
import matplotlib.lines

sns.set_theme()


class ElenaAnalysis(data_loading.LoadData):
    """Docstring for ElenaAnalysis. """
    def __init__(self, data_path, config_file=None):
        """TODO: to be defined. """
        data_loading.LoadData.__init__(self,
                                       data_path=data_path,
                                       config_file=config_file)

    def plot_pee_counts(self, ax=None):
        if ax is None:
            fig, ax = plt.subplots(figsize=(15, 10))

        min_time = self._df_pee["datetime"].min()
        mean_time = self._df_pee["datetime"].mean()
        max_time = self._df_pee["datetime"].max()
        timedelta = max_time - min_time
        bins = timedelta.days + 1
        min_time = min_time.replace(hour=0, minute=0, second=0)
        max_time = max_time.replace(day=max_time.day + 1,
                                    hour=0,
                                    minute=0,
                                    second=0)
        custom_bins = pd.date_range(start=min_time,
                                    end=max_time).to_pydatetime().tolist()
        ax.hist(self._df_pee["datetime"], bins=custom_bins)
        plt.xticks(rotation=90)
        plt.xlabel("date")
        plt.ylabel("counts")

    def plot_day(self,
                 month_to_plot,
                 start_cut,
                 end_cut,
                 df_feed,
                 df_pee,
                 ax=None,
                 change_label_coords=True,
                 plot_mica=False,
                 plot_windel=False,
                 ):
        if ax is None:
            fig, ax = plt.subplots(figsize=(15, 10), nrows=1, ncols=1)
        day = start_cut.day
        for idx, (start,
                  end) in enumerate(zip(df_feed["start"], df_feed["end"])):
            ax.axvspan(start, end,
                       **self.config["plotting_config"]["kwargs_feed"])
        for pee, mica, windel in zip(df_pee["datetime"], df_pee["Mica"],
                                     df_pee["Windel"]):
            if plot_mica:
                if mica is not None:
                    if mica:
                        ax.axvline(
                            pee, **self.config["plotting_config"]
                            ["kwargs_pee_mica"])
                    else:
                        ax.axvline(
                            pee, **self.config["plotting_config"]
                            ["kwargs_pee_no_mica"])
            if plot_windel:
                if windel is not None:
                    if windel == "trocken":
                        ax.axvline(
                            pee, **self.config["plotting_config"]
                            ["kwargs_pee_trocken_windel"])
                    else:
                        ax.axvline(
                            pee, **self.config["plotting_config"]
                            ["kwargs_pee_no_trocken_windel"])

        ax.set_xlim(start_cut, end_cut)
        bed_time = start_cut.replace(hour=self._numbers_config["bedtime"])
        ax.axvline(bed_time, **self.config["plotting_config"]["bedtime_colors"])
        getup_time = start_cut.replace(hour=self._numbers_config["getuptime"])
        ax.axvline(getup_time, **self.config["plotting_config"]["bedtime_colors"])
        ax.set_yticks([])
        ax.set_ylabel(day, rotation=0, labelpad=15)
        if change_label_coords:
            ax.yaxis.set_label_coords(-0.02, 0.1)

    def plot_month(self, year, month, plot_mica=False, plot_windel=False, add_legend=True):
        month_details = monthrange(year, month)
        fig, axs = plt.subplots(figsize=(15, 10),
                                nrows=month_details[1],
                                ncols=1)

        start_cut = datetime(year=year, month=month, day=1, hour=0, minute=0)
        end_cut = start_cut + relativedelta(months=+1)

        month_year = start_cut.strftime("%B - %Y")
        fig.suptitle("Overview of month {info}".format(info=month_year),
                     fontsize=20)
        custom_bins = pd.date_range(start=start_cut,
                                    end=end_cut).to_pydatetime().tolist()
        for idx, (ax, start_cut, end_cut) in enumerate(
                zip(axs, custom_bins[:-1], custom_bins[1:])):
            this_pee = self._df_pee[(self._df_pee["datetime"] > start_cut)
                                    & (self._df_pee["datetime"] < end_cut)]
            this_feed = self._df_feed[(self._df_feed["end"] > start_cut)
                                      & (self._df_feed["start"] < end_cut)]
            self.plot_day(month_to_plot=month,
                                    start_cut=start_cut,
                                    end_cut=end_cut,
                                    df_feed=this_feed,
                                    df_pee=this_pee,
                                    ax=ax,
                                    plot_windel=plot_windel,
                                    plot_mica=plot_mica)
            if idx != len(axs) - 1:
                ax.set_xticks([])
            else:
                myFmt = mdates.DateFormatter('%H')
                ax.xaxis.set_major_formatter(myFmt)
                ax.set_xlabel("Hours of the day")

        if add_legend:
            handles, labels = self.create_legend(plot_mica, plot_windel)
            axs[0].legend(handles=handles, labels=labels, ncol=6, bbox_to_anchor=(0.5, 3.5), loc='upper center')

        figname = f"activity_{month_year}.png"
        plt.savefig(figname, dpi=300)

    def create_legend(self, plot_mica, plot_windel):
        feed = matplotlib.lines.Line2D(xdata=[0], ydata=[0], **self.config["plotting_config"]["kwargs_feed"])
        mica = matplotlib.lines.Line2D(xdata=[0], ydata=[0], **self.config["plotting_config"]["kwargs_pee_mica"])
        nomica = matplotlib.lines.Line2D(xdata=[0], ydata=[0], **self.config["plotting_config"]["kwargs_pee_no_mica"])
        windel = matplotlib.lines.Line2D(xdata=[0], ydata=[0], **self.config["plotting_config"]["kwargs_pee_trocken_windel"])
        nowindel = matplotlib.lines.Line2D(xdata=[0], ydata=[0], **self.config["plotting_config"]["kwargs_pee_no_trocken_windel"])
        bedtime = matplotlib.lines.Line2D(xdata=[0], ydata=[0], **self.config["plotting_config"]["bedtime_colors"])

        handles = [feed]
        if plot_mica:
            handles.append(mica)
            handles.append(nomica)
        if plot_windel:
            handles.append(windel)
            handles.append(nowindel)
        handles.append(bedtime)
        labels = [h.get_label() for h in handles]
        return handles, labels


