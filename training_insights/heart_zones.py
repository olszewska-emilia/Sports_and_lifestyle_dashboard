class HeartZoneClassifier:
    def __init__(self, df, column="heart_rate@bpm"):
        self.original_df = df.copy()
        self.column = column
        self.df = df.copy()
        self.mean = self.df[self.column].mean()
        self.std = self.df[self.column].std()
        self.lower_bound = self.mean - 3 * self.std
        self.upper_bound = self.mean + 3 * self.std
        self.HR_max = None

    def filter_outliers(self):
        self.df = self.df[(self.df[self.column] >= self.lower_bound) & (self.df[self.column] <= self.upper_bound)].copy()
        if not self.df.empty:
            self.HR_max = self.df[self.column].max()
        else:
            self.HR_max = 0
        return self.df

    def classify_heart_rate(self, hr_value):
        if self.HR_max == 0:
            return None
        ratio = hr_value / self.HR_max
        if ratio < 0.5:
            return 0
        elif ratio < 0.6:
            return 1
        elif ratio < 0.7:
            return 2
        elif ratio < 0.8:
            return 3
        elif ratio < 0.9:
            return 4
        else:
            return 5

    def assign_zones(self):
        if self.HR_max is None:
            self.filter_outliers()
        self.df["zone"] = self.df[self.column].apply(self.classify_heart_rate)
        return self.df

    def summary(self):
        return {
            "mean_heart_rate": self.mean,
            "std_dev_heart_rate": self.std,
            "lower_bound": self.lower_bound,
            "upper_bound": self.upper_bound,
            "HR_max_after_filter": self.HR_max
        }
