# Data Cleaning Report: Employee Dataset

## Overview
- Source: `employees_raw.csv` (19 rows x 8 columns)
- Output: `employees_clean.csv` (17 rows x 9 columns, 0 missing values)

## Issues found in the raw data
| Issue | Where |
|---|---|
| Missing values | age (2), salary (2), performance_score (2) |
| Duplicate rows | 2 exact duplicates |
| Wrong data types | salary stored as text (commas), age contains text, join_date contains 'not available' |
| Inconsistent text | mixed case and trailing spaces in department/city |
| Invalid value | negative age (-5) |

## Cleaning steps applied
1. **Standardise text:** Stripped whitespace from name/department/city and applied Title Case (fixes 'engineering', 'pune', 'Pune ', 'Engineering ').
2. **Remove duplicates:** Dropped 2 exact duplicate rows (emp_id 102 and 105 were repeated).
3. **Fix data types:** salary: removed thousands separators -> numeric; age: coerced to numeric (1 non-numeric value turned into NaN); join_date: converted to datetime ('not available' -> NaT); department and city: converted to category.
4. **Invalid values:** Set 1 impossible age value(s) (e.g. -5) to NaN so they are imputed with the rest.
5. **Missing values:** age and performance_score -> filled with column median; salary -> filled with department median; join_date -> filled with median join date. Missing cells filled: 9.

## Basic statistics (cleaned data)
| column | mean | median | std | min | max |
|---|---|---|---|---|---|
| age | 34.29 | 33.0 | 6.64 | 26.0 | 52.0 |
| salary | 68529.41 | 65000.0 | 16624.97 | 45000.0 | 105000.0 |
| performance_score | 3.94 | 3.9 | 0.39 | 3.2 | 4.6 |
| tenure_years | 7.47 | 6.4 | 3.0 | 3.5 | 13.9 |

### Value counts: department
| department | count |
|---|---|
| Engineering | 6 |
| Finance | 4 |
| Marketing | 4 |
| HR | 3 |

### Value counts: city
| city | count |
|---|---|
| Pune | 6 |
| Delhi | 3 |
| Mumbai | 3 |
| Bengaluru | 2 |
| Chennai | 1 |
| Hyderabad | 1 |
| Kolkata | 1 |

### Salary by department
| department | mean | median |
|---|---|---|
| Engineering | 68167.0 | 69000.0 |
| Finance | 93750.0 | 91000.0 |
| HR | 48000.0 | 47000.0 |
| Marketing | 59250.0 | 59000.0 |

## Key takeaways
- Average salary is 68,529 vs median 65,000; the mean is higher because a few Finance salaries pull it up.
- Largest department: Engineering (6 employees); most common city: Pune (6).

## Assumptions and caveats
- Median imputation was chosen over mean because it is robust to outliers; with only a few records, imputed values are estimates and should be flagged in real analyses.
- Duplicates were detected on full-row equality only.
