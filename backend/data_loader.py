import csv

class FoodData:
    def __init__(self, csv_path):
        self.by_chinese ={}
        self.by_label= {}
        self.load_csv(csv_path)

    def load_csv(self, csv_path):
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                label = row.get("label","").strip()
                chinese = row.get("chinese_name","").strip()
                try:
                    sodium = float(row.get("sodium_per_100g",0))
                except ValueError:
                    sodium = 0.00
                if chinese:
                    self.by_chinese[chinese] = sodium
                if label and chinese:
                    self.by_label[label] = (chinese,sodium)


    def get_all_chinese(self):
        return list(self.by_chinese.keys())

    def get_sodium_by_chinese(self, chinese_name):
        return self.by_chinese.get(chinese_name)

    def get_by_label(self, label):
        return self.by_label.get(label,(None,None))