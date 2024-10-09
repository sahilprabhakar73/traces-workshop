import math


"""
Score based filtering based on the exponential decay function. This drastically decreases the score for the segment with low number of points and are of small duration. The scoring function could be further extended to factor in speed or other available or computed parameters as well.

"""


def calculate_score(
    segment_duration,
    segment_points,
    duration_decay_rate=0.01,
    points_decary_rate=0.1,
    duration_weight=0.7,
    points_weight=0.3,
):
    # Apply exponential scaling to segment duration and available points
    scaled_duration = 1 - math.exp(-duration_decay_rate * segment_duration)
    scaled_points = 1 - math.exp(-points_decary_rate * segment_points)

    # Calculate the final score
    score = (duration_weight * scaled_duration) + (points_weight * scaled_points)

    return score
