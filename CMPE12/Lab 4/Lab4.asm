.ORIG x3000
; ** Program **
Start ;
	; Clearing all registers
	AND R0, R0, 0
	AND R1, R1, 0
	AND R2, R2, 0
	AND R3, R3, 0
	AND R4, R4, 0
	AND R5, R5, 0
	AND R6, R6, 0
	AND R7, R7, 0
	JSR SubClearArray ; Clear the array memory
	
	LD R0, StrWelcomeAddr
	PUTS
	JSR SubGet ; Get input
	; Check what the input is (D/E/X)
	LD R2, ASCIIX 	; Check X
	ADD R1, R0, R2 	; Load result to R1
	BRz Exit
	LD R2, ASCIIE 	; Check E
	ADD R1, R0, R2 	; Load result to R1
	BRz Encrypt
	LD R2, ASCIID 	; Check D
	ADD R1, R0, R2 	; Load result to R1
	BRz Decrypt
	BR Restart
	
Encrypt ;
	JSR SubCipherInput
	
	LD R0, StrInputAddr
	PUTS
	LD R4, ASCIILF
	AND R1, R1, 0 ; Clear R1, is r counter
	AND R2, R2, 0 ; Clear R2, is c counter (increment this)
	AND R3, R3, 0 ; Clear R3
EncryptInput ;
	JSR SubGet
	ADD R3, R0, 0 ; Copy R0 to R3
	ADD R3, R4, R3 ; Check if character is LF
	BRz EncryptEnd
	; If not, store character (R0: char, R1: r, R2: c)
	JSR SubStore
	; Now encrypt each character as they type it, and store it in row 1
	JSR SubEncrypt
	ADD R1, R1, 1
	JSR SubStore
	ADD R1, R1, -1 ; Reset row to 0 to store unencrypted
	
	ADD R2, R2, 1 ; Increment c
	BR EncryptInput ; Loop
	
EncryptEnd ;
		
	; Print out the array. Prints row 1 and 2
	JSR SubPrintArray
	BR Restart

Decrypt ;
	JSR SubCipherInput
	
	LD R0, StrInputAddr
	PUTS
	LD R4, ASCIILF
	AND R1, R1, 0 ; Clear R1, is r counter
	AND R2, R2, 0 ; Clear R2, is c counter (increment this)
	AND R3, R3, 0 ; Clear R3
DecryptInput ;
	JSR SubGet
	ADD R3, R0, 0 ; Copy R0 to R3
	ADD R3, R4, R3 ; Check if character is LF
	BRz DecryptEnd
	; If not, store character (R0: char, R1: r, R2: c)
	JSR SubStore
	; Now decrypt each character as they type it, and store it in row 0
	JSR SubDecrypt
	ADD R1, R1, 1
	JSR SubStore
	ADD R1, R1, -1 ; Reset row to 0 to store unencrypted
	
	ADD R2, R2, 1 ; Increment c
	BR DecryptInput ; Loop
	
DecryptEnd ;
		
	; Print out the array. Prints row 1 and 2
	JSR SubPrintArray
	BR Restart

Restart ;
	LD R0, ASCIILFPrint
	OUT
	BR Start
	
Exit ;
	LD R0, ASCIILFPrint
	OUT
	LD R0, StrByeAddr
	PUTS
	HALT
END
HALT

; ** Variables **

ASCIINumOff 	.FILL	-48
ASCIIUpOff		.FILL	-65
ASCIILoOff		.FILL	-97
ASCIID			.FILL	-68
ASCIIE			.FILL	-69
ASCIIX			.FILL	-88
ASCIILF			.FILL	-10
ASCIILFPrint	.FILL	10
AlphabetMax		.FILL	26
ArrayCol		.FILL	200

; Memory Locations
SaveR0			.FILL	0
SaveR1			.FILL	0
SaveR2			.FILL	0
SaveR3			.FILL	0
SaveR4			.FILL	0
SaveR5			.FILL	0
SaveR6			.FILL	0
SaveR7			.FILL	0
SaveR7Mul		.FILL	0
SaveR7Get		.FILL	0
SaveR7Clear		.FILL	0
ShiftVal		.FILL 	0

; So we can print these without having them clutter up our variable space
StrWelcomeAddr	.FILL	StrWelcome
StrCipherAddr	.FILL	StrCipher
StrByeAddr		.FILL	StrBye
StrInputAddr	.FILL	StrInput
StrEncryptAddr	.FILL	StrEncrypt
StrDecryptAddr	.FILL 	StrDecrypt
StrDecryptedAddr .FILL	StrDecrypted
StrEncryptedAddr .FILL	StrEncrypted

Array			.FILL	x4000 ; Memory location of the first value in the 2x200 array

; ** End Variables **

; ** Subs **
; Encrypt Sub (R0 char/output) ShiftVal in memory
; This sub takes the input character and shifts it by ShiftVal
; Also makes sure to wrap around. Returns encrypted char in R0
; Don't alter characters outside of a-z,A-Z
SubEncrypt
	ST R1, SaveR1
	ST R2, SaveR2
	ST R3, SaveR3
	ST R4, SaveR4
	ST R5, SaveR5
	ST R6, SaveR6
	ST R7, SaveR7
	
	LD R2, AlphabetMax
	; Check if we should do nothing (special character)
	; char > 'z' (BRp) (A)
	LD R4, ASCIILoOff
	NOT R2, R2
	ADD R2, R2, 1 ; -AlphabetMax
	ADD R1, R2, R4 ; R1 <- AsciiLo + AlphabetMax
	ADD R5, R0, R1 ; R5 <- Char - 'z'
	BRzp SubEncryptEnd
	
	; (B)
	; c < 'Z' && c > 'a'
	LD R4, ASCIIUpOff
	ADD R1, R2, R4 ; UpOff+AlphabetMax = 'Z'
	ADD R5, R0, R1 ; R5 <- char - 'Z'
	BRzp SubEncryptCheckC
	BR SubEncryptCheckD
	
SubEncryptCheckC ; (C) 2nd part of (B)
	LD R4, ASCIILoOff
	ADD R5, R0, R4 ; char - loOffset ('a')
	BRn SubEncryptEnd
	
SubEncryptCheckD ; char < 'A'
	LD R4, ASCIIUpOff
	ADD R5, R0, R4 ; char - 'A'
	BRn SubEncryptEnd
	
	; If we get to here, then the character is A-Z|a-Z
	; Check if lower
	LD R4, ASCIILoOff
	ADD R5, R0, R4 ; char - AsciiLo
	BRzp SubEncryptLower	; if it's 0 or positive then it should be lowercase
	BR SubEncryptUpper 		; if it's not lower, it must be uppercase
	
SubEncryptLower ;
	LD R3, ShiftVal ; Load cipher shift
	LD R4, ASCIILoOff
	BR SubEncryptShift

SubEncryptUpper ;
	LD R3, ShiftVal ; Load cipher shift
	LD R4, ASCIIUpOff
	BR SubEncryptShift
	
SubEncryptShift ;
	ADD R5, R0, R4 ; R5 <- 0-26 value of the character
	ADD R5, R5, R3 ; Add shift to character
	; Check if shifted value is greater than AlphabetMax (R2)
	ADD R1, R5, R2 ; char - 26
	BRzp SubEncryptOverlap ; It's bigger
	BR SubEncryptEnd
SubEncryptOverlap ; 
	ADD R5, R1, 0 ; Copy R1's value to R5, because that's the new shift
	
SubEncryptEnd ;
	NOT R4, R4
	ADD R4, R4, 1
	ADD R0, R5, R4 ; R0 <- AsciiOffset + NumberChar. This is our actual shifted, overlapped, ascii character
	
	LD R1, SaveR1
	LD R2, SaveR2
	LD R3, SaveR3
	LD R4, SaveR4
	LD R5, SaveR5
	LD R6, SaveR6
	LD R7, SaveR7
RET
; Decrypt Sub (R0 char/output) shift in memory
; Must shift characters backwards by ShiftVal amount
; Make sure to test for underlap and wrap backwards
SubDecrypt
	ST R1, SaveR1
	ST R2, SaveR2
	ST R3, SaveR3
	ST R4, SaveR4
	ST R5, SaveR5
	ST R6, SaveR6
	ST R7, SaveR7
	
	LD R2, AlphabetMax
	; Check if we should do nothing (special character)
	; char > 'z' (BRp) (A)
	LD R4, ASCIILoOff
	NOT R2, R2
	ADD R2, R2, 1 ; -AlphabetMax
	ADD R1, R2, R4 ; R1 <- AsciiLo + AlphabetMax
	ADD R5, R0, R1 ; R5 <- Char - 'z'
	BRzp SubDecryptEnd
	
	; (B)
	; c < 'Z' && c > 'a'
	LD R4, ASCIIUpOff
	ADD R1, R2, R4 ; UpOff+AlphabetMax = 'Z'
	ADD R5, R0, R1 ; R5 <- char - 'Z'
	BRzp SubDecryptCheckC
	BR SubDecryptCheckD
	
SubDecryptCheckC ; (C) 2nd part of (B)
	LD R4, ASCIILoOff
	ADD R5, R0, R4 ; char - loOffset ('a')
	BRn SubDecryptEnd
	
SubDecryptCheckD ; char < 'A'
	LD R4, ASCIIUpOff
	ADD R5, R0, R4 ; char - 'A'
	BRn SubDecryptEnd
	
	
	; If we get to here, then the character is A-Z|a-Z
	; Check if lower
	LD R4, ASCIILoOff
	ADD R5, R0, R4 ; char - AsciiLo
	BRzp SubDecryptLower	; if it's 0 or positive then it should be lowercase
	BR SubDecryptUpper 		; if it's not lower, it must be uppercase
	
SubDecryptLower ;
	LD R3, ShiftVal ; Load cipher shift
	LD R4, ASCIILoOff
	BR SubDecryptShift
	
SubDecryptUpper ;
	LD R3, ShiftVal ; Load cipher shift
	LD R4, ASCIIUpOff
	BR SubDecryptShift
	
SubDecryptShift ;
	ADD R5, R0, R4 ; R5 <- 0-26 value of the character
	NOT R3, R3
	ADD R3, R3, 1 ; 2SC Shift, since we need to subtract
	ADD R5, R5, R3 ; Add shift to character
	; Check if shifted value is less than 0
	BRn SubDecryptOverlap ; We need to wrap backwards
	BR SubDecryptEnd
SubDecryptOverlap ;
	NOT R2, R2 
	ADD R2, R2, 1 ; Revert AlphabetMax to positive
	ADD R5, R5, R2 ; AlphabetMax - shift
	
SubDecryptEnd ;
	NOT R4, R4
	ADD R4, R4, 1
	ADD R0, R5, R4 ; R0 <- AsciiOffset + NumberChar. This is our actual shifted, overlapped, ascii character
	
	LD R1, SaveR1
	LD R2, SaveR2
	LD R3, SaveR3
	LD R4, SaveR4
	LD R5, SaveR5
	LD R6, SaveR6
	LD R7, SaveR7
RET

; Print Array
SubPrintArray
	ST R0, SaveR0
	ST R1, SaveR1
	ST R7, SaveR7
	
	; Print first col
	LD R0, StrDecryptedAddr
	PUTS
	LD R0, Array
	PUTS
	; Print LF
	LD R0, ASCIILFPrint
	OUT
	; Print second col
	LD R0, StrEncryptedAddr
	PUTS
	LD R0, Array
	LD R1, ArrayCol ; Offset is +200
	ADD R1, R1, 1 	; It's off-by-1
	ADD R0, R1, R0 
	PUTS
	
	LD R0, SaveR0
	LD R1, SaveR1
	LD R7, SaveR7
RET

; We need to make sure the memory is actually clear before we write to it for the first time
; This sub can only be called first, because it uses a lot of the same registers that Store does
;  and I don't feel like saving them
SubClearArray
	ST R7, SaveR7Clear
	
	AND R0, R0, 0 ; Make sure to store 0
	AND R1, R1, 0 ; r=0
	AND R2, R2, 0 ; c=0
	LD R3, ArrayCol ; Number of slots per col
	
SubClear ;
	JSR SubStore
	ADD R2, R2, 1 ; Increment col
	ADD R3, R3, -1 ; Decrement total slots
	BRz SubClearCheck
	BR SubClear
	
SubClearCheck ;
	ADD R1, R1, 0
	BRp SubClearEnd ; if val is 1, then we've looped twice
	ADD R1, R1, 1
	AND R2, R2, 0
	LD R3, ArrayCol
	BR SubClear ; Go back to the top with R1=0 and R2=1
	
SubClearEnd
	
	LD R7, SaveR7Clear
RET

; Store (data: R0, r: R1, c: R2) Sub: Row Major
	; BaseAddr + (r*m) + c =  R3 + (R1*m) + R2
SubStore
	ST R7, SaveR7
	ST R1, SaveR1
	ST R2, SaveR2
	ST R3, SaveR3
	ST R4, SaveR4
	
	LD R3, Array ; R3 Running Mem Location
	ADD R3, R3, R2 ; R3 + R2(c)
	ADD R1, R1, 0 	; Multiply R1(r) by 200 (Either 0 or 200, since r is 0,1)
	BRz SubStoreCont ; If r is 0, skip the multiplying
SubStoreMult ; Add 200 to R1
	LD R4, ArrayCol
	ADD R1, R1, R4
SubStoreCont ;
	ADD R3, R1, R3
	STR R0, R3, 0 ; mem[R3] <- R0	
	
	LD R1, SaveR1
	LD R2, SaveR2
	LD R3, SaveR3
	LD R4, SaveR4
	LD R7, SaveR7
RET
; Load (data output: R0, r: R1, c: R2) Sub: Row Major
SubLoad
	ST R7, SaveR7
	ST R1, SaveR1
	ST R2, SaveR2
	ST R3, SaveR3
	ST R4, SaveR4
	
	LD R3, Array ; Array mem location
	ADD R3, R3, R2 ; R3 + R2(c)
	ADD R1, R1, 0 	; Multiply R1(r) by 200 (Either 0 or 200, since r is 0,1)
	BRz SubLoadCont ; If r is 0, skip the multiplying
SubLoadMult ; Add 200 to R1
	LD R4, ArrayCol
	ADD R1, R1, R4
SubLoadCont ;
	ADD R3, R1, R3
	LDR R0, R3, 0 ; R0 <- mem[R3]
	
	LD R1, SaveR1
	LD R2, SaveR2
	LD R3, SaveR3
	LD R4, SaveR4
	LD R7, SaveR7
RET
; Get (GETC + OUT)
SubGet
	ST R7, SaveR7Get
	GETC
	OUT
	LD R7, SaveR7Get
RET

; Get input 1-25 for the offset
SubCipherInput ;
	ST R7, SaveR7
	ST R3, SaveR3
	ST R4, SaveR4
	ST R5, SaveR5
	ST R6, SaveR6
	
	LD R0, StrCipherAddr ; Load message and print
	PUTS
	LD R4, ASCIILF 	; Load LF and number offset
	LD R5, ASCIINumOff
	AND R3, R3, 0 ; Clear
	AND R6, R6, 0 ; Clear
	LD R3, ShiftVal ; Clear shift value in memory
CipherInput ;
	JSR SubGet
	ADD R3, R0, 0 ; Copy R0 to R3
	ADD R3, R3, R4 ; Check for LF
	BRz CipherInputEnd
	; Else, store input
	ADD R0, R0, R5 ; Convert to number
	ADD R3, R0, 0  ; Copy R0 to R3
	ADD R0, R6, 0  ; Copy current total (R6) to R0
	BRp CipherMult ; If it's not the first number, multiply R0 by 10 to get right number places
	
CipherMultCont
	ADD R6, R0, R3 ; R6 = R3(current number) + R0(Old num that's beenn *10, or 0). Add it to running sum
	BR CipherInput
	
CipherMult ;
	JSR SubMult10 ; R0 * 10
	BR CipherMultCont
	
CipherInputEnd ;
	ST R6, ShiftVal ; mem[ShifVal] <- R6(running sum)
	LD R3, SaveR3
	LD R4, SaveR4
	LD R5, SaveR5
	LD R6, SaveR6
	LD R7, SaveR7
RET

; Multiply R0 by 10
SubMult10
	; Add R0 to R1 10 times
	; Use R3 to keep track of loops
	ST R3, SaveR3 ; mem[SaveR3] <- R3
	ST R1, SaveR1 ; mem[SaveR1] <- R1
	ST R7, SaveR7Mul
	AND R3, R3, 0 ; Clear R3
	AND R1, R1, 0
	ADD R3, R3, 10 ; R3 <- 10
MultLoop
	BRz MultEnd ; If R3 == 0
	ADD R1, R0, R1; R1=R0+R1
	ADD R3, R3, -1 ; R3-1
	BR MultLoop
MultEnd
	AND R0, R0, 0 ; Clear R0
	ADD R0, R1, 0 ; Copy R0 <- R1
	LD R3, SaveR3 ; R3 <- mem[SaveR3]
	LD R1, SaveR1 ; R1 <- mem[SaveR1]
	LD R7, SaveR7Mul
RET


; Strings
StrWelcome 		.STRINGZ "Welcome to the cipher program\nDo you want to (E)ncrypt, (D)ecrypt, or e(X)it?\n"
StrCipher	 	.STRINGZ "\nWhat's the cipher? (1-25)"
StrBye			.STRINGZ "Goodbye"
StrInput		.STRINGZ "Enter string (up to 200 chars)"
StrEncrypt 		.STRINGZ "Your string, and the encryption"
StrDecrypt		.STRINGZ "Your string, and the decryption"
StrEncrypted	.STRINGZ "<Encrypted> "
StrDecrypted	.STRINGZ "<Decrypted> "



.END