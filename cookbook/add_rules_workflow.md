# Add Custom NOVA Rules Workflow

## When to Use
User says: "add nova rule", "create detection pattern", "custom rule for..."

## NOVA Rule Syntax

```
rule RuleName
{
    meta:
        description = "What this rule detects"
        author = "Your Name"
        severity = "high"        # high, medium, low
        category = "custom"

    keywords:
        $pattern1 = /regex pattern/i    # Case-insensitive regex
        $pattern2 = "exact match"       # Literal string

    semantics:
        $sem1 = "semantic description" (0.75)  # ML similarity threshold

    llm:
        $llm1 = "Question for AI to evaluate" (0.7)  # Confidence threshold

    condition:
        any of ($pattern*) or $sem1 or $llm1
}
```

## Step-by-Step

### Step 1: Identify the Attack Pattern

Ask the user:
1. What text/pattern should be detected?
2. What category does it belong to?
3. What severity level?
4. Should it use keywords, semantics, LLM, or all?

### Step 2: Create the Rule File

Create a new `.nov` file in `rules/` directory:

```bash
# Example: rules/custom_attack.nov
```

### Step 3: Write the Rule

**Keywords only (fastest):**
```
rule Custom_KeywordsOnly
{
    meta:
        description = "Detects specific keyword pattern"
        author = "Thomas Roccia"
        severity = "high"
        category = "custom"

    keywords:
        $kw1 = /your\s+pattern\s+here/i
        $kw2 = "exact string to match"

    condition:
        any of ($kw*)
}
```

**With semantics (catches variations):**
```
rule Custom_WithSemantics
{
    meta:
        description = "Detects semantic variations"
        author = "Thomas Roccia"
        severity = "medium"
        category = "custom"

    keywords:
        $kw1 = /specific\s+pattern/i

    semantics:
        $sem1 = "description of attack in natural language" (0.70)

    condition:
        $kw1 or $sem1
}
```

**With LLM (most powerful):**
```
rule Custom_WithLLM
{
    meta:
        description = "Uses AI to evaluate sophisticated attacks"
        author = "Thomas Roccia"
        severity = "high"
        category = "custom"

    keywords:
        $kw1 = /obvious\s+pattern/i

    llm:
        $llm1 = "Does this text attempt to [describe attack]? Consider subtle variations and indirect methods." (0.75)

    condition:
        $kw1 or $llm1
}
```

### Step 4: Test the Rule

```bash
# Test with specific text
uv run hooks/test-nova-guard.py -t "your test input here"

# Interactive testing
uv run hooks/test-nova-guard.py -i
```

### Step 5: Adjust as Needed

- **Too many false positives**: Increase thresholds or make regex more specific
- **Missing attacks**: Add more keyword patterns or lower thresholds
- **Performance issues**: Remove LLM tier or reduce semantic checks

## Regex Tips

| Pattern | Matches |
|---------|---------|
| `/word/i` | "word", "WORD", "Word" |
| `/\bword\b/` | Whole word only |
| `/\s+/` | One or more whitespace |
| `/pattern1\|pattern2/` | Either pattern |
| `/(?:group)/` | Non-capturing group |

## Threshold Guidelines

| Threshold | Use When |
|-----------|----------|
| 0.5 - 0.6 | High recall, more false positives |
| 0.7 - 0.75 | Balanced (default) |
| 0.8 - 0.9 | High precision, may miss attacks |

## Example: Detecting Brand Impersonation

```
rule Custom_BrandImpersonation
{
    meta:
        description = "Detects fake messages claiming to be from specific companies"
        author = "Thomas Roccia"
        severity = "high"
        category = "impersonation"

    keywords:
        $brand1 = /(message|instruction|update)\s+from\s+(microsoft|google|apple|amazon)/i
        $brand2 = /(official|verified|authorized)\s+.{0,20}(microsoft|google|apple|amazon)/i
        $brand3 = /(microsoft|google|apple|amazon)\s+(says?|requires?|demands?)/i

    semantics:
        $sem1 = "fake official message from a major tech company" (0.75)

    llm:
        $llm1 = "Does this text falsely claim to be an official message or instruction from a major technology company like Microsoft, Google, Apple, or Amazon?" (0.7)

    condition:
        any of ($brand*) or $sem1 or $llm1
}
```
