.ORIG X3000

LEA R0, Welcome
PUTS

Start ;
; Clearing registers, just to be sure
AND R0, R0, 0
AND R1, R1, 0
AND R2, R2, 0
AND R3, R3, 0
AND R4, R4, 0
LEA R4, MemInput

LEA R0, Prompt
PUTS

Input ;
GETC

ADD R1, R0, 0	; Copy input into R1

; Check if input is X, and if so convert to binary.
NOT R0, R0		; Turn input negative
ADD R0, R0, 1

LD R6, MemX		; Bring X back into R6 from memory
ADD R7, R6, R0 	; If these are equal the answer should be zero, which means the user entered X

BRz Quit
; R0 is 2SC input, R1 is original input, R6 is X, R2 is loop counter, R4 is memory location of stored inputs

	; We didn't quit, so check for LF or number input
	LD R6, MemLF
	ADD R7, R6, R0
	BRz Convert ; If user entered LF, convert the number stored to binary
	
	; They didn't enter LF, so store the input
	; Store number inputted.	
	STR R1, R4, 0 ; mem[R4+0] <- R1
	ADD R0, R1, 0 ; Echo character
	OUT
	ADD R4, R4, 1 ; Increment memory location
	ADD R2, R2, 1 ; Keep track of the number of numbers that have been inputted
	
	LD R6, MaxNum; Check if the number is too large
	NOT R6, R6
	ADD R6, R6, 1 ; 2SC
	ADD R0, R6, R2 ; R0 <- R2 - R6
	BRz Overflow ; If they've exceeded the max number, move to converting
	
	BR Input ; Jump back to getting input
	

; Only R3 is sum, R2 is loop counter
Convert ; Convert the number into binary.
	LD R0, MemLF ; Load the LF and print
	OUT
	LEA R0, ConvertMsg
	PUTS
	; We need to take all the individual numbers and add them up into one number
	; We'll load them into R3
	LD R6, ASCIIOff ; Load Ascii Offset
	LEA R4, MemInput ; Reset the memory location counter to the first number
					; So we're not reading it backwards
					
	; Check if the first character is a - sign
	LDR R0, R4, 0
	LD R1, ASCIIMinus
	NOT R0, R0		; 2SC first input for testing
	ADD R0, R0, 1
	ADD R1, R1, R0
	BRnp CombineNumbers ; It isn't, so move on
	; It is, so flip the InputNeg value
	ADD R1, R1, 1 ; R1 must be 0 here
	ST R1, InputNeg ; mem[InputNeg] <- R1
	ADD R4, R4, 1 ; Increment memory loc to ignore the - sign and get to the numbers
	ADD R2, R2, -1 ; Decrement loop counter so we don't go running off into memory
	
	CombineNumbers ;
		LDR R0, R4, 0 ; R0 <- mem[R4]
		ADD R4, R4, 1 ; Increment memory location for next loop load if needed
		ADD R0, R0, R6 ; Convert from ascii to numeric
		ADD R3, R0, R3 ; R3 <- R3 + R0
		ADD R2, R2, -1 ; Decrement loop counter
		
		BRz ConvertNumbers ; If loop counter (R2) == 0, go to the converting
					; If we need to add more numbers, add another place to the sum
		JSR MultR310 ; R3*10 to keep the proper place values
		BR CombineNumbers ; Else, continue combining
		
	ConvertNumbers ;
		; R3 holds our combined number, all else is free to use
		; First, check if our number is negative. If it is, 2SC it
		LD R0, InputNeg ; If the number is negative, this will be 1, else 0
		BRz CN_Cont ; If 0, do nothing
		NOT R3, R3
		ADD R3, R3, 1 ; 2SC the input number
		
	CN_Cont
		LD R2, MaxNum ; Load loop counter back into R2 at max
		NOT R2, R2
		ADD R2, R2, 1 ; Convert loop counter to negative
		AND R1, R1, 0 ; Clear R1, it's going to be our bitmask loop counter offset
		LD R4, BitMask
		
		CN_Loop ;
			; If R1 == R2, then we're done
			ADD R0, R1, R2
			BRz CN_LoopEnd
			
			AND R0, R3, R4 ; AND Input and bitmask
			
			BRz Bit_Zero ; If AND is zero, display that
			BR  Bit_One ; Else, show a 1
		
		Bit_Zero ; Show a zero
			LD R0, ASCIIZero
			OUT
			ADD R3, R3, R3 ; Left shift the value
			ADD R1, R1, 1 ; Increment loop counter
			BR CN_Loop
		Bit_One ; Show a one
			LD R0, ASCIIOne
			OUT
			ADD R3, R3, R3 ; Left shift the value
			ADD R1, R1, 1 ; Increment loop counter
			BR CN_Loop
		CN_LoopEnd
			LD R0, MemLF ; Display newline and restart program
			OUT
			BR Start
			
	BR Start ; Restart input

Overflow ; 
	LEA R0, OutOfNumbers
	PUTS
	BR Convert
	
Quit ;
	LEA R0, YesQuit
	PUTS
	HALT
END
HALT
; ************
; Lables below
; ************

; Memory locations
MemX 		.FILL 88 ; X in ASCII
MemLF 		.FILL 10 ; Given by hitting enter
ASCIIOff 	.FILL -48 ; ASCII Offset for numbers
ASCIIZero 	.FILL 48
ASCIIOne 	.FILL 49
ASCIIMinus 	.FILL 45 ; Negative sign (-)
SaveR0		.FILL 0 ; Location to save R0 to
SaveR1		.FILL 0

MaxNum		.FILL 16 ; Max number given the bitmasks
BitMask 	.FILL b1000000000000000 ; 32768

InputNeg	.FILL 0	; Is the input number negative? (0=no, 1=yes)
MemLoops 	.FILL 0
MemInput 	.FILL 1 ; Locations to store number input
			.FILL 1
			.FILL 1
			.FILL 1
			.FILL 1
			.FILL 1
			.FILL 1
			.FILL 1
			.FILL 1
			.FILL 1
			.FILL 1
			.FILL 1
			.FILL 1
			.FILL 1
			.FILL 1
			.FILL 1
; Strings
Welcome .STRINGZ "Decimal to Binary Conversion\n"
Prompt .STRINGZ "Enter decimal number (0-9 or -) or X to quit:\n"
YesQuit .STRINGZ "You entered X. Quitting.\n"
ConvertMsg .STRINGZ "Converting to binary...\n"
OutOfNumbers .STRINGZ "\nCan't handle a number larger than that."

; Subs
; Multiply R3 by 10
MultR310
	; Add R3 to R1 10 times
	; Use R0 to keep track of loops
	ST R0, SaveR0 ; mem[SaveR0] <- R0
	ST R1, SaveR1 ; mem[SaveR1] <- R1
	AND R0, R0, 0 ; Clear R0
	AND R1, R1, 0
	ADD R0, R0, 10 ; R0 <- 10
MultLoop
	BRz MultEnd ; If R0 == 0
	ADD R1, R3, R1; R1=R3+R1
	ADD R0, R0, -1 ; R0-1
	BR MultLoop
MultEnd
	AND R3, R3, 0 ; Clear R3
	ADD R3, R1, 0 ; Copy R3 <- R1
	LD R0, SaveR0 ; R0 <- mem[SaveR0]
	LD R1, SaveR1 ; R1 <- mem[SaveR1]
RET

.END