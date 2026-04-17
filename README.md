# PSI-MOD Curator

Validation and curation tools for the [PSI-MOD](https://github.com/HUPO-PSI/psi-mod-CV) protein modification ontology. Focuses on structure validation using RDKit, cross-reference checking, and mass/formula consistency.

## Installation

```bash
uvx psimod-validator
```

or

```bash
pipx run psimod-validator
```

## Usage

### Command Line

```bash
# Validate entire ontology
psimod-validator validate PSI-MOD.obo

# Validate and auto-fix issues (writes PSI-MOD.fixed.obo)
psimod-validator validate PSI-MOD.obo --fix

# Strict mode (warnings become errors)
psimod-validator validate PSI-MOD.obo --strict

# JSON or Markdown output
psimod-validator validate PSI-MOD.obo --format json -o report.json

# Check specific terms
psimod-validator check --ontology PSI-MOD.obo MOD:00046 MOD:00047

# Verify cross-references online (slow)
psimod-validator validate PSI-MOD.obo --check-online
```

### Python API

```python
from psimod_validator import PsiModValidator

validator = PsiModValidator("PSI-MOD.obo")
report = validator.validate_all()

print(f"Errors: {report.error_count}")
print(f"Warnings: {report.warning_count}")
print(f"Fixable: {len(report.fixable_issues)}")

for issue in report.errors:
    print(f"{issue.mod_id}: [{issue.category}] {issue.message}")
```

## Validation Rules

| Category | What it checks | Severity |
|----------|---------------|----------|
| **SMILES** | Parseable by RDKit, canonical form, valence errors, undefined stereocenters | ERROR / WARNING |
| **Backbone** | Dummy atom patterns via SMARTS, term_spec consistency | WARNING / ERROR |
| **Mass** | SMILES-computed mass/formula vs MassMono/Formula annotations | ERROR (fixable) |
| **Charge** | RDKit formal charge vs FormalCharge annotation | ERROR (fixable) |
| **Xref** | Unimod/UniProt PTM/Origin format, optional online verification | ERROR / WARNING |
| **Structure** | Term name, definition, parent relationships | ERROR / WARNING / INFO |
