# BlueBox technical docs

This is a list of prototypes for the functions that make up the Blue Abstraction Layer (BAL) of Apple's BlueBox. BAL function names start with "BAL" and seem to be safe to call from any code, 68k or PowerPC.

PowerPC CFM code should just link to BlueAbstractionLayerLib and call the desired functions that way. Classic 68k code must statically link to some glue that wraps the FE22 trap like so:

```
	(push four-byte arguments)
	MOVE.L	#selector,d0
	DC.W	$FE22
```

Note that "selector" is a long, when the selectors are actually shorts. This is to allow the number for four-byte arguments to be passed in the high word, as a stack-blowout-prevention method. By scraping these motifs from shipped 68k code, we have been able to determine the argument count for over 100 of the 602 BAL calls.

All BAL functions return a single 32-bit value.