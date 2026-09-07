# Stars! J-RC3 Parity Notes

## Population Growth

Status: DOCUMENTED / PARTIALLY SPECIFIED

### Confirmed behavior

For a planet with positive habitability:

- racial maximum growth rate is specified as a percentage per year;
- at 100% habitability, population may grow at the race's full growth rate;
- lower positive habitability scales the growth rate proportionally;
- growth begins to slow after the planet reaches 25% of its population capacity;
- population capacity is based on habitability.

For negative habitability:

- population dies each year;
- annual death percentage is `abs(habitability) / 10`.

### Maximum population

For an ordinary race on a 100% world:

    1,000,000

Known modifiers:

- Hyper-Expansion: 500,000
- Jack-of-All-Trades: 1,200,000
- Only Basic Remote Mining: +10% capacity

Positive worlds below 5% habitability are treated as 5% for
population-capacity purposes.

### Unknown / needs measurement

- Exact growth formula above 25% capacity.
- Exact rounding behavior.
- Exact order of operations between:
  - habitability modifier
  - racial growth rate
  - crowding modifier
- Exact behavior at 100% capacity.
- Exact overcrowding death curve between 100% and 400%.
- Integer population units used internally by J-RC3.

### Sources

- Stars! User Manual, Population / Growth Rate / Maximum Population /
  Overcrowding / Killer Planets sections.

### Tests

TBD.
