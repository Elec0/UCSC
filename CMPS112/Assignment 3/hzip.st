#!/afs/cats.ucsc.edu/courses/cmps112-wm/usr/smalltalk/bin/gst -f
"CMPS 112: Assignment 3
 Aaron Steele (atsteele)
 Madeline Conner (mjconner)"

"1. Load frequency table ----------------------------------------------"
nl := Character nl.

Character extend [
   isPrint [
      ^ ($! <= self) & (self <= $~)
   ]
   "Print the character as if it's printable, else print in octal"
   visible [
      | stringReturn |
      self isPrint ifTrue: [^ ' ', self asString, ' ' ]
                   ifFalse: 
                      [(self asInteger = 256) 
                         ifTrue: [^ 'EOF']
                         ifFalse: [stringReturn := 'x', 
                       (self asInteger printPaddedWith:$0 to:2 base:16).
                        ^ stringReturn]]
   ]
]

Object subclass: ZeroArray [
   |theArray|

   ZeroArray class >> new [
      self shouldNotImplement.
   ]

   ZeroArray class >> new: size [
      |result|
      result := super new.
      result init: size.
      ^ result
   ]

   init: size [
      theArray := Array new: size.
   ]

   size [
      ^ theArray size.
   ]

   at: index [
      ^ theArray at: index + 1.
   ]

   at: index put: value [
      ^ theArray at: index + 1 put: value.
   ]

   incr: index [
      (self at: index) isNil
         ifTrue: [ self at: index put: 0].
      self at: index put: (self at: index) + 1.
   ]

   keysAndValuesDo: aBlock [
      (0 to: (self size) - 1) do: [:index |
         aBlock value: index value: (self at: index).
      ]
   ]

]

"Leaf object, has character and count.
Will only ever be an actual leaf. Not interior node."
Object subclass: Leaf [
   |char count isLeaf|
   char [ ^ char ]
   count [ ^ count ]
   isLeaf [ ^ isLeaf]
   
   Leaf class >> new [
      self shouldNotImplement
   ]

   Leaf class >> new: aChar count: aCount [
      |result|
      result := super new.
      result setChar: aChar andCount: aCount.
      ^result
   ]

   setChar: aChar andCount: aCount [
      char := aChar.
      count := aCount.
      isLeaf := true.
   ]

   "For the SortedCollection to properly sort lexigraphically"
   <= other [
      count = other count
         ifTrue: [^ char <= other char]
         ifFalse: [^ count <= other count].
   ]

   "Use the Character visible to print"
   printBase: aStream [
      ^ aStream << self class << '(' << char asCharacter visible 
                << ',' << count
   ]

   printOn: aStream [
      (self printBase: aStream) << ')'.
   ]

   inorder: visitor prefix: string [
      visitor value: char value: string.
   ]
  
   postorder: visitor prefix: bit postfix: pbit [
      visitor value: char value: '0' value: pbit.
   ]

]

Leaf subclass: Tree [
   |left right| "The left and right leaves"
   left  [^left]
   right [^right]
   isLeaf [ ^ isLeaf]
   
   "Tree constructor, with the root character and aggregate count"
   Tree class >> new: aChar count: aCount [
      self shouldNotImplement
   ]

   "Tree constructor with the same, but also left and right leaves"
   Tree class >> new: aChar count: aCount left: aLeft right: aRight [
      |result|
      result := super new: aChar count: aCount.
      result setLeft: aLeft andRight: aRight.
      ^ result
   ]

   setLeft: aLeft andRight: aRight [
      left := aLeft.
      right := aRight.
      isLeaf := false.
   ]

   "Print the tree out"
   printOn: aStream [
      (self printBase: aStream) << ',' << left << ',' << right << ')'.
   ]

   "Print every 0 and 1 path to every leaf?"
   inorder: visitor prefix: string [
      left inorder: visitor prefix: string, '0'.
      right inorder: visitor prefix: string, '1'.
   ]
 
   postorder: visitor prefix: bit postfix: pbit [
      left postorder: visitor prefix: '' postfix: ''.
      right postorder: visitor prefix: '' postfix: pbit,'1'.
   ]
]

"Outputs bits to a given file."
Object subclass: OutBits [
   |bitIndex currentByte myStream|
   OutBits class >> new [
      self shouldNotImplement.
   ]
   OutBits class >> new: fileStream [
      |result|
      result := super new.
      result init: fileStream.
      ^result
   ]
   clearByte [
      bitIndex := 8.
      currentByte := 0.
   ]
   init: fileStream [
      myStream := fileStream.
      self clearByte.
   ]
   flushByte [
      bitIndex = 8 ifFalse: [
         myStream nextPutByte: currentByte.
         self clearByte.
      ]
   ]
   writeBit: bit [
      currentByte := currentByte bitAt: bitIndex put: bit.
      bitIndex := bitIndex - 1.
      bitIndex = 0 ifTrue: [self flushByte].
   ]
]

Object subclass: BitStream [
   |bitIndex byte myStream|
   BitStream class >> new: fileStream [
      |result|
      result := super new.
      result init: fileStream.
      ^result
   ]
   init: fileStream [
      myStream := fileStream.
      bitIndex := 1.
   ]
   nextBit [
      bitIndex = 1 ifTrue: [
         byte := myStream next.
         bitIndex := 9.
      ].
      bitIndex := bitIndex - 1.
      ^byte value bitAt: bitIndex
   ]
   atEnd [
      ^bitIndex = 1 and: [myStream atEnd]
   ]
]

"--------------------------------------------"

"This is the main computational part, need to specify
 1. the inputfile, 2. the output file, 3. which argument to use"
main := [:infile :outfile :arg|
   "The output variable is a string that is a bitstring we will convert
   to actual binary at the end."
   output := ''.
   
   (arg = '-t' or: [arg = '-c']) ifTrue: [
   "Create and load the frequency table"
   freqtable := ZeroArray new: 257.
   pathtable := ZeroArray new: 257.

   [infile atEnd not] whileTrue: [
      |ordChar|
      ordChar := infile next asInteger.
      freqtable incr: ordChar.
   ].

   freqtable incr: 256.

   "Print the frequency table"
"   freqtable keysAndValuesDo: [:key :value |
      (value notNil and: [value > 0]) ifTrue: [
         outfile << 'freq[' << key asCharacter visible << ']=' 
                 << value << nl.
      ]
   ].
"
   "Create and load the priority queue from the frequency table"
   priority := SortedCollection new.

   freqtable keysAndValuesDo: [:key :value |
      (value notNil and: [value > 0]) ifTrue: [
         priority add: (Leaf new: key count: value).
      ]
   ].

  " outfile << nl << 'Printing the priority queue:' << nl.
   priority do: [:item| stdout << item <<nl.].

   outfile << nl << 'Now adding leaves and making a tree' << nl.
"
   "While the priority queue has at least 2 elements,
   keep removing the smallest two and creating a tree out of those 
   elements, then reinsterting the tree into the queue."
   [priority size >= 2] whileTrue:
      [z := Tree new: ((priority at: 1)char) 
         count: (((priority at: 1)count) + ((priority at: 2)count))   
         left: (priority at: 1) right: (priority at: 2).
      priority remove: (priority at: 1).
      "The list moves the second element to the front after removing."
      priority remove: (priority at: 1).
      priority add: z.
   "   outfile << nl << 'Tree is - ' << z << nl.
      outfile << nl << 'Printing the priority queue:' << nl.
      priority do: [:item| stdout << item <<nl.]."
      ].

   "If -t option is provided, we need to print out the frequency table
    in an organized manner. Here is some code to figure out the values
    for testing, which should then be adjusted to actually print out
    the frequency table instead.
    We need this to be called even on -c because we use the pathtable
    for compressing. Only print on -t."
   freqtable keysAndValuesDo: [:key :value |
      (value notNil and: [value > 0]) ifTrue: [
         (priority at: 1) inorder: [:char :string |
            (key = char) ifTrue: [
               pathtable at: char asInteger put: string.
            (arg = '-t') ifTrue: [ "Only print if -t"
               outfile << 
               char asCharacter visible <<
               (value asInteger printPaddedWith:$ to: 8) <<
               '  ' << string << nl.
            ].
         ]. ] prefix: ''.
      ].
   ].
   
   
   "Compress a file."
   (arg = '-c') ifTrue: [
      (priority at:1) postorder: [:char :bit :pbit |
         "Print the chartacter as bitstring"
         bchar := ''.
         (char = 256) ifTrue: [ bchar := '000000001']
                      ifFalse: [ (char = 0)
                        ifTrue: [ bchar := '000000000' ]
                        ifFalse: [ bchar := 
                       (char asInteger printPaddedWith:$0 to:8 base:2)]
                     ].
         output := output, bit, bchar, pbit.
         
      ] prefix: '' postfix: ''. 
      output:= output, '1'. "MAYBE"
      
      "output := output, '|'."
      
      infile reset. "Reset the pointer to top of file."
      [infile atEnd not] whileTrue: [
         |ordChar path|
         ordChar := infile next asInteger.
         "Get the path to a character from the pathtable"
         path := pathtable at: ordChar asInteger.
         output := output, path.
      ].
      
      output := output, (pathtable at: 256).
      
      "Actually write the bitstring to the file as bytes"
      outBytes := OutBits new: outfile.
      "Loop over each character in the bitstring and write those bits."
      count := 8.
      output do: [:char| outBytes writeBit: char asInteger. 
         count := count-1. ].
      outBytes flushByte.
      
      "stdout << 'OUTPUT: ' << output << nl.
      stdout << (priority at:1) <<nl."
   ].
    
   ].
   
   "Uncompressing the file."
   (arg = '-u') ifTrue: [
      |stoploop nextbyte nextbit bit bitinput stack tRight tLeft nt ptr|
      
      stack := OrderedCollection new.
      bitinput := BitStream new: infile.
      stoploop := false.
      
      "Rebuild decoding tree loop"
      [(bitinput atEnd not) & (stoploop not)] whileTrue: [
         bit := bitinput nextBit.
         (bit = 0) ifTrue: [
            nextbyte := 0.
            "Loop from 8 to 1 and read bits"
            8 to:1 by:-1 do:[:i|
               nextbit := bitinput nextBit.
               nextbyte := nextbyte bitAt:i put:nextbit.
               "stdout << 'i: ' << i << ' bit: ' << nextbit << nl."
            ].
            (nextbyte = 0) ifTrue: [
               nextbit := bitinput nextBit.
               (nextbit = 1) ifTrue: [nextbyte := 256]
                             ifFalse: [nextbyte := 0]
            ].
               
            stack add: (Leaf new: nextbyte asCharacter count:0).
            "stdout << 'stack add: ' << nextbyte << nl."
            nextbyte := 0.
            ]
            ifFalse: [ "bit = 1"
            (stack size = 1) ifTrue: [stoploop := true.]
                             ifFalse: [
                  tRight := stack removeLast.
                  tLeft := stack removeLast.
                  nt := Tree new: $ count: 0 
                     left: tLeft right: tRight.
                  stack add: nt.
               ].
            "stdout << stack << nl.
            stdout << 'stack size: ' << stack size << nl."
            ].
      ].
      "stdout << stack << nl."
      
      "Actual decoding loop"
      stoploop := false.
      ptr := stack at:1.
      [(bitinput atEnd not) & (stoploop not)] whileTrue: [
         "If the pointer is at a leaf, 
         print it and reset pointer to top of tree."
         (ptr isLeaf) ifTrue: [
            "If the leaf char is EOF, stop the loop."
            (ptr char asInteger = 256) ifTrue: [stoploop := true]
               ifFalse: [
                  outfile nextPut: 
                     (Character value: (ptr char asInteger)).
                  ptr := stack at:1.
               ]
         ]
         "Pointer is not at a leaf, 
         so read bit to determine where to move."
         ifFalse: [ "(ptr is not leaf)"
            bit := bitinput nextBit.

            (bit = 0) ifTrue: [
               ptr := ptr left.
            ]
            ifFalse: [ "(bit = 1)"
               ptr := ptr right.
            ].
         ]
      ].
   ].

].


"The user needs to specify exactly 2 or 3 arguments, otherwise error."
((Smalltalk arguments size > 1) & (Smalltalk arguments size < 4))
   ifTrue: [infile := FileStream open: (Smalltalk arguments at: 2) 
                                 mode: FileStream read.
            argOption := (Smalltalk arguments at: 1).
            Smalltalk arguments size = 2 
            ifTrue: [ main value: infile 
                           value: stdout 
                           value: argOption.
                    ]
            ifFalse: [outfile := FileStream 
                           open: (Smalltalk arguments at: 3) 
                           mode: FileStream write.
                      main value: infile
                           value: outfile
                           value: argOption.
                     ].
            infile close.]
   ifFalse: [stderr << 'Need to specify an input file and exactly' <<
                      ' one flag: -dtcu.' << nl.
            stderr flush.].
