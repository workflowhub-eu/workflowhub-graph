import sys


def update_progress_bar(progress: int, total: int, bar_length: int = 50):
    """
    Updates the progress bar.

    :param progress: Current progress.
    :param total: The total value when the progress is complete.
    :param bar_length: The length of the progress bar in characters.
    """
    fraction = progress / total
    arrow = int(fraction * bar_length) * "="
    padding = int(bar_length - len(arrow)) * " "
    percent = int(fraction * 100)
    sys.stdout.write(f"\r[{arrow}{padding}] {percent}%")
    sys.stdout.flush()
