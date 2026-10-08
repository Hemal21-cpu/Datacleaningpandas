"""Data Cleaning & Exploration with Pandas.

Loads employees_raw.csv, cleans it, prints basic statistics, writes
employees_clean.csv and cleaning_report.md.
"""
import pandas as pd
import numpy as np

RAW = "employees_raw.csv"
CLEAN = "employees_clean.csv"
REPORT = "cleaning_report.md"

log = []  # (step, detail) pairs for the report

# ---------------------------------------------------------------- 1. LOAD
df = pd.read_csv(RAW)
print("=== RAW DATA ===")
print(df.head(10), "\n")
print("Shape:", df.shape)
print("\nDtypes before cleaning:\n", df.dtypes)
print("\nMissing values before cleaning:\n", df.isna().sum(), "\n")

raw_rows = len(df)
raw_dtypes = df.dtypes.astype(str).to_dict()
raw_missing = df.isna().sum().to_dict()

# ------------------------------------------- 2. TEXT STANDARDISATION
# Trim whitespace and normalise case so "engineering " == "Engineering".
for col in ["name", "department", "city"]:
    df[col] = df[col].str.strip()
df["department"] = df["department"].str.title().replace({"Hr": "HR"})
df["city"] = df["city"].str.title()
log.append(("Standardise text",
            "Stripped whitespace from name/department/city and applied Title Case "
            "(fixes 'engineering', 'pune', 'Pune ', 'Engineering ')."))

# ------------------------------------------------------- 3. DUPLICATES
dups = df.duplicated().sum()
df = df.drop_duplicates().reset_index(drop=True)
log.append(("Remove duplicates",
            f"Dropped {dups} exact duplicate rows (emp_id 102 and 105 were repeated)."))

# ---------------------------------------------- 4. FIX DATA TYPES
# salary: strings such as "65,000" / "1,05,000" (Indian digit grouping)
df["salary"] = pd.to_numeric(df["salary"].astype(str).str.replace(",", "", regex=False),
                             errors="coerce")
# age: "twenty-eight" cannot be parsed -> NaN
bad_age_text = pd.to_numeric(df["age"], errors="coerce").isna() & df["age"].notna()
df["age"] = pd.to_numeric(df["age"], errors="coerce")
# join_date: "not available" -> NaT
df["join_date"] = pd.to_datetime(df["join_date"], errors="coerce")
df["department"] = df["department"].astype("category")
df["city"] = df["city"].astype("category")
log.append(("Fix data types",
            "salary: removed thousands separators -> numeric; "
            f"age: coerced to numeric ({bad_age_text.sum()} non-numeric value turned into NaN); "
            "join_date: converted to datetime ('not available' -> NaT); "
            "department and city: converted to category."))

# ------------------------------------------ 5. INVALID VALUES
invalid_age = (df["age"] < 18) | (df["age"] > 70)
n_invalid = int(invalid_age.sum())
df.loc[invalid_age, "age"] = np.nan
log.append(("Invalid values",
            f"Set {n_invalid} impossible age value(s) (e.g. -5) to NaN so they are imputed with the rest."))

# ---------------------------------------------- 6. MISSING VALUES
before_missing = df.isna().sum()
# Numeric columns: median (robust to outliers such as the highest salaries)
df["age"] = df["age"].fillna(df["age"].median())
df["performance_score"] = df["performance_score"].fillna(df["performance_score"].median())
# Salary: median of the person's department is more realistic than the global median
df["salary"] = df["salary"].fillna(df.groupby("department", observed=True)["salary"].transform("median"))
# Dates: fill with the median join date
df["join_date"] = df["join_date"].fillna(df["join_date"].sort_values().iloc[len(df["join_date"].dropna()) // 2])
df["age"] = df["age"].round().astype(int)
log.append(("Missing values",
            "age and performance_score -> filled with column median; "
            "salary -> filled with department median; "
            "join_date -> filled with median join date. "
            f"Missing cells filled: {int(before_missing.sum())}."))

# ------------------------------------------------ 7. FEATURE (bonus)
df["tenure_years"] = ((pd.Timestamp("2026-10-08") - df["join_date"]).dt.days / 365.25).round(1)

# --------------------------------------------------- 8. STATISTICS
print("=== CLEANED DATA ===")
print(df, "\n")
print("Dtypes after cleaning:\n", df.dtypes, "\n")
print("Missing after cleaning:", int(df.isna().sum().sum()), "\n")

num_cols = ["age", "salary", "performance_score", "tenure_years"]
stats = pd.DataFrame({
    "mean": df[num_cols].mean(),
    "median": df[num_cols].median(),
    "std": df[num_cols].std(),
    "min": df[num_cols].min(),
    "max": df[num_cols].max(),
}).round(2)
print("=== BASIC STATISTICS ===")
print(stats, "\n")

dept_counts = df["department"].value_counts()
city_counts = df["city"].value_counts()
print("Value counts - department:\n", dept_counts, "\n")
print("Value counts - city:\n", city_counts, "\n")

dept_salary = df.groupby("department", observed=True)["salary"].agg(["mean", "median"]).round(0)
print("Salary by department:\n", dept_salary, "\n")

df.to_csv(CLEAN, index=False)

# ------------------------------------------------------- 9. REPORT
def md_table(frame, index_name=""):
    frame = frame.reset_index()
    frame.columns = [index_name if i == 0 and index_name else c for i, c in enumerate(frame.columns)]
    head = "| " + " | ".join(map(str, frame.columns)) + " |"
    sep = "|" + "---|" * len(frame.columns)
    rows = ["| " + " | ".join(str(v) for v in r) + " |" for r in frame.values]
    return "\n".join([head, sep] + rows)

lines = [
    "# Data Cleaning Report: Employee Dataset",
    "",
    "## Overview",
    f"- Source: `{RAW}` ({raw_rows} rows x 8 columns)",
    f"- Output: `{CLEAN}` ({len(df)} rows x {df.shape[1]} columns, 0 missing values)",
    "",
    "## Issues found in the raw data",
    "| Issue | Where |",
    "|---|---|",
    f"| Missing values | {', '.join(f'{k} ({v})' for k, v in raw_missing.items() if v)} |",
    f"| Duplicate rows | {dups} exact duplicates |",
    "| Wrong data types | salary stored as text (commas), age contains text, join_date contains 'not available' |",
    "| Inconsistent text | mixed case and trailing spaces in department/city |",
    "| Invalid value | negative age (-5) |",
    "",
    "## Cleaning steps applied",
]
for i, (step, detail) in enumerate(log, 1):
    lines.append(f"{i}. **{step}:** {detail}")
lines += [
    "",
    "## Basic statistics (cleaned data)",
    md_table(stats, "column"),
    "",
    "### Value counts: department",
    md_table(dept_counts.rename("count").to_frame(), "department"),
    "",
    "### Value counts: city",
    md_table(city_counts.rename("count").to_frame(), "city"),
    "",
    "### Salary by department",
    md_table(dept_salary, "department"),
    "",
    "## Key takeaways",
    f"- Average salary is {stats.loc['salary','mean']:,.0f} vs median {stats.loc['salary','median']:,.0f}; "
    "the mean is higher because a few Finance salaries pull it up.",
    f"- Largest department: {dept_counts.index[0]} ({dept_counts.iloc[0]} employees); "
    f"most common city: {city_counts.index[0]} ({city_counts.iloc[0]}).",
    "",
    "## Assumptions and caveats",
    "- Median imputation was chosen over mean because it is robust to outliers; with only a few "
    "records, imputed values are estimates and should be flagged in real analyses.",
    "- Duplicates were detected on full-row equality only.",
]
with open(REPORT, "w") as f:
    f.write("\n".join(lines) + "\n")
print(f"Saved {CLEAN} and {REPORT}")
