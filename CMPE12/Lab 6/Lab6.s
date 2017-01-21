 /* Name: Aaron Steele
    Class: CMPE 12/L
    Lab: 6
*/
#include <WProgram.h>

#include <xc.h>
/* define all global symbols here */
.global main
.global read
.text
.set noreorder

.ent main
main:
    /* this code blocks sets up the ability to print, do not alter it */
   ADDIU $v0,$zero,1
    LA $t0,__XC_UART
    SW $v0,0($t0)
    LA $t0,U1MODE
    LW $v0,0($t0)
    ORI $v0,$v0,0b1000
    SW $v0,0($t0)
    LA $t0,U1BRG
    ADDIU $v0,$zero,12
    SW $v0,0($t0)

    
    
    LA $a0,WelcomeMessage
    JAL puts
    NOP
    
    
    /* your code goes underneath this */
    LA $a0, inNumericString
    LI $t1, 0 # Clear t0, is dec output
    LI $t3, 10
    LI $t4, 0 # Neg flag. 1=neg
    
    # Check if negative
    LB $t0, 0($a0)
    BNE $t0, 45, convStr # Branch if 1st byte isn't '-'
    NOP
    ADDI $t4, $t4, 1 # Set neg flag to 1
    ADDI $a0, $a0, 1
convStr:
    LB $t0, 0($a0)
    BEQ $t0, 0, convStrEnd # If loaded byte is 0, we're done
    NOP
    ADDI $t0, $t0, -48 # Sub ascii num offset
    MULT $t1, $t3   # Mult t1 by 10. If t1 is 0, it doesnt matter, if not it moves place over
    MFLO $t1	    # Get result, put into t1
    ADD $t1, $t1, $t0	# Add to running total
    ADDI $a0, $a0, 1
    B convStr
    NOP
convStrEnd:
    BEQ $t4, 0, convStrFin
    NOP
    SUBU $t1, $0, $t1 # Make num neg
convStrFin:
    # t1 should hold the dec number here.
    LI $t0, 0b1 # Initial mask
    LA $a1, outBinaryString
    LA $a0, outBinaryString
    ADDI $a1, $a1, 31	# We're writing to the end of the string to start with, so add 31 to bring us to the end
    ADDI $a0, $a0, -1	# Need this to make sure we dont end on the last value and don't convert it
convBin:
    BEQ $a1, $a0, convBinEnd # Branch if we reached our starting address
    NOP
    AND $t3, $t0, $t1	# And the mask and the value
    ADDI $t3, $t3, 48	# Convert back into ascii
    SB $t3, 0($a1)	# Store ascii 0 or 1 into memory location
    ADDI $a1, $a1, -1	# Add -1 to a1 to increment location
    SRL $t1, $t1, 1	# Shift value 1 to the right
    B convBin
    NOP
convBinEnd:
    
    /* your code goes above this */
    
    LA $a0,DecimalMessage
    JAL puts
    NOP
    LA $a0,inNumericString
    JAL puts
    NOP
    
    LA $a0,BinaryMessage
    JAL puts
    NOP
    LA $a0,outBinaryString
    JAL puts
    NOP
    
    

    
    

endProgram:
    J endProgram
    NOP
.end main




.data
WelcomeMessage: .asciiz "Welcome to the converter\n"
DecimalMessage: .asciiz "The decimal number is: "
BinaryMessage: .asciiz "The binary number is: "
    
inNumericString: .asciiz "255"
outBinaryString: .asciiz "zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz"


