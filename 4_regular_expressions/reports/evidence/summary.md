# Lab 4 Analysis Bundle

## Meta

- Variants covered: 4
- Expressions covered: 12
- Repeat cap: 5
- Sample count per expression: 4
- Benchmark iterations: 5
- Heaviest bounded expression: variant 3 / expression 3 (29120 rough paths)

## Variant 1

### Expression 1

- Regex: `(a|b)(c|d)E+G?`
- Validation target: `^(?:a|b)(?:c|d)(?:E)+(?:G)?$`
- Metrics: nodes=11, depth=3, alternations=2, repeats=2, rough_paths=40
- Benchmark: parse_ms=0.028, generate_ms=0.0305, validate_ms=0.0224
- Generated samples: `acE, acEG, acEE, acEEG`
- Official examples: `acEG, bdE, adEEG`
- Trace sample: `acEEE`

### Expression 2

- Regex: `P(Q|R|S)T(UV|W|X)*Z+`
- Validation target: `^P(?:Q|R|S)T(?:(?:UV|W|X))*(?:Z)+$`
- Metrics: nodes=16, depth=5, alternations=2, repeats=2, rough_paths=5460
- Benchmark: parse_ms=0.053, generate_ms=0.0506, validate_ms=0.0196
- Generated samples: `PQTZ, PQTZZ, PQTZZZ, PQTZZZZ`
- Official examples: `PQTUVUVZ, PRTWWWWZ`
- Trace sample: `PSTZZZZZ`

### Expression 3

- Regex: `1(0|1)*2(3|4)^5(3)(6)`
- Validation target: `^1(?:(?:0|1))*2(?:(?:3|4)){5}36$`
- Metrics: nodes=13, depth=4, alternations=2, repeats=2, rough_paths=2016
- Benchmark: parse_ms=0.0805, generate_ms=0.0706, validate_ms=0.0289
- Generated samples: `123333336, 123333436, 123334336, 123334436`
- Official examples: `1023333336, 1124444436`
- Trace sample: `1101124433436`

## Variant 2

### Expression 1

- Regex: `M?N^2(O|P)^3Q*R+`
- Validation target: `^(?:M)?(?:N){2}(?:(?:O|P)){3}(?:Q)*(?:R)+$`
- Metrics: nodes=13, depth=4, alternations=1, repeats=5, rough_paths=480
- Benchmark: parse_ms=0.0346, generate_ms=0.0684, validate_ms=0.0319
- Generated samples: `NNOOOR, NNOOORR, NNOOORRR, NNOOORRRR`
- Official examples: `MNNOOOQR, NNPPPQQQRRR`
- Trace sample: `NNOPOQQR`

### Expression 2

- Regex: `(X|Y|Z)^3(8)+(9|0)`
- Validation target: `^(?:(?:X|Y|Z)){3}(?:8)+(?:9|0)$`
- Metrics: nodes=11, depth=4, alternations=2, repeats=2, rough_paths=270
- Benchmark: parse_ms=0.0369, generate_ms=0.0392, validate_ms=0.0135
- Generated samples: `XXX89, XXX80, XXX889, XXX880`
- Official examples: `XXX89, YYY88889`
- Trace sample: `YZZ89`

### Expression 3

- Regex: `(H|I)(J|K)L*N?`
- Validation target: `^(?:H|I)(?:J|K)(?:L)*(?:N)?$`
- Metrics: nodes=11, depth=3, alternations=2, repeats=2, rough_paths=48
- Benchmark: parse_ms=0.027, generate_ms=0.0374, validate_ms=0.0161
- Generated samples: `HJ, HJN, HJL, HJLN`
- Official examples: `HJLLN, IKLLLLLL`
- Trace sample: `IJLLLN`

## Variant 3

### Expression 1

- Regex: `O(P|Q|R)+2(3|4)`
- Validation target: `^O(?:(?:P|Q|R))+2(?:3|4)$`
- Metrics: nodes=11, depth=4, alternations=2, repeats=1, rough_paths=726
- Benchmark: parse_ms=0.0347, generate_ms=0.0276, validate_ms=0.0136
- Generated samples: `OP23, OP24, OQ23, OQ24`
- Official examples: `OPP23, OQQQQ24`
- Trace sample: `ORPRR23`

### Expression 2

- Regex: `A*B(C|D|E)F(G|H|I)^2`
- Validation target: `^(?:A)*B(?:C|D|E)F(?:(?:G|H|I)){2}$`
- Metrics: nodes=14, depth=4, alternations=2, repeats=2, rough_paths=162
- Benchmark: parse_ms=0.0355, generate_ms=0.0419, validate_ms=0.0113
- Generated samples: `BCFGG, BCFGH, BCFGI, BCFHG`
- Official examples: `AAABCFGG, AAAAAABDFHH`
- Trace sample: `AAAABDFGG`

### Expression 3

- Regex: `J+K(L|M|N)*O?(P|Q)^3`
- Validation target: `^(?:J)+K(?:(?:L|M|N))*(?:O)?(?:(?:P|Q)){3}$`
- Metrics: nodes=15, depth=4, alternations=2, repeats=4, rough_paths=29120
- Benchmark: parse_ms=0.0407, generate_ms=0.0597, validate_ms=0.0154
- Generated samples: `JKPPP, JKPPQ, JKPQP, JKPQQ`
- Official examples: `JJKLOPPP, JKNQQQ`
- Trace sample: `JKNPQP`

## Variant 4

### Expression 1

- Regex: `(S|T)(U|V)W*Y+24`
- Validation target: `^(?:S|T)(?:U|V)(?:W)*(?:Y)+24$`
- Metrics: nodes=13, depth=3, alternations=2, repeats=2, rough_paths=120
- Benchmark: parse_ms=0.0385, generate_ms=0.0676, validate_ms=0.0482
- Generated samples: `SUY24, SUYY24, SUYYY24, SUYYYY24`
- Official examples: `SUWWY24, SVWY24`
- Trace sample: `SUWWYYY24`

### Expression 2

- Regex: `L(M|N)O^3P*Q(2|3)`
- Validation target: `^L(?:M|N)(?:O){3}(?:P)*Q(?:2|3)$`
- Metrics: nodes=13, depth=3, alternations=2, repeats=2, rough_paths=24
- Benchmark: parse_ms=0.0415, generate_ms=0.0547, validate_ms=0.0299
- Generated samples: `LMOOOQ2, LMOOOQ3, LMOOOPQ2, LMOOOPQ3`
- Official examples: `LMOOOPPPQ2, LNOOOPQ3`
- Trace sample: `LMOOOPPPPPQ2`

### Expression 3

- Regex: `R*S(T|U|V)W(X|Y|Z)^2`
- Validation target: `^(?:R)*S(?:T|U|V)W(?:(?:X|Y|Z)){2}$`
- Metrics: nodes=14, depth=4, alternations=2, repeats=2, rough_paths=162
- Benchmark: parse_ms=0.1118, generate_ms=0.082, validate_ms=0.0306
- Generated samples: `STWXX, STWXY, STWXZ, STWYX`
- Official examples: `RSTWXX, RRRSUWYY`
- Trace sample: `RRSUWYY`
