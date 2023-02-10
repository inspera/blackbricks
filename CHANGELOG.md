## 2.0.0 (2023-02-10)

### BREAKING CHANGE

- add newline at the end of formatted notebooks (#36)

## 1.0.5 (2023-02-07)

### Fix

- **deps**: bump oauthlib from 3.2.1 to 3.2.2 (#35)

## 1.0.4 (2023-01-31)

### Fix

- avoid failing on quoted cell dividers

## 1.0.3 (2023-01-31)

Resolve buf where blackbricks removed sql code on the same line as the `%sql` magic. See #32.

## 1.0.2 (2023-01-10)

Bumping dependencies to resolve dependabot alert. See #30.

## 1.0.1 (2022-10-28)

Non-functional patch with minor documentation updates.

## 1.0.0 (2022-09-12)

### Fix

- respect `insecure` option in .databrickscfg (#28)
- restore Python 3.8 compatibility
- handle trailing whitespace the same as Databricks
- add strict mypy typing to project
- ignore non-text files

### Feat

- recursively discover remote notebooks
- remove option for two-space indentation

### BREAKING CHANGE

Removal of two-space indentation as an option and the change to forcing the PEP-8 compliant four-space indentation.

See [#25](https://github.com/inspera/blackbricks/pull/25) for background.

## 0.7.0 (2022-09-03)

### Feat

- deprecate two-space indentation

## 0.6.7 (2021-08-04)

### Fix

- gracefully skip emtpy files

## 0.6.6 (2021-05-27)

### Fix

- handle cell titles in magic cells

## 0.6.5 (2021-05-27)

### Fix

- update docstring handling with upstream changes in black

