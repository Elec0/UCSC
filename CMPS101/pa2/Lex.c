#define _CRT_SECURE_NO_DEPRECATE
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include "List.h"

#define MAX_LEN 160

//int strcmp(const char*, const char*);

int main(int argc, char * argv[]) {    
    int i = 0;
    FILE *in, *out;
    char lines[MAX_LEN][BUFSIZ];


    // check command line for correct number of arguments
    if (argc != 3) {
        printf("Usage: %s <input file> <output file>\n", argv[0]);
        exit(1);
    }

    // open files for reading and writing 
    in = fopen(argv[1], "r");
    out = fopen(argv[2], "w");
    if (in == NULL) {
        printf("Unable to open file %s for reading\n", argv[1]);
        exit(1);
    }
    if (out == NULL) {
        printf("Unable to open file %s for writing\n", argv[2]);
        exit(1);
    }
    
    while (i < MAX_LEN && fgets(lines[i], sizeof(lines[0]), in))
    {
        lines[i][strlen(lines[i]) - 1] = '\0';
        i = i + 1;
    }
    
    List L = newList();

    for (int j = 0; j < i; ++j)
    {
        // Use insertion sort method from front to back
        moveFront(L);

        while (index(L) >= 0)
        {
            // if next string comes after current
            if (strcmp(lines[j], lines[get(L)]) > 0)
            {
                moveNext(L);
            }
            else // If next string comes before or is equal to string, place before
            {
                insertBefore(L, j);
                break;
            }
        }

        // If cursor falls off list, append to list
        if (index(L) < 0)
            append(L, j);
    }


    // Write to file
    moveFront(L);
    while (index(L) >= 0)
    {
        fprintf(out, "%s\n", lines[get(L)]);
        moveNext(L);
    }

    /* close files */
    fclose(in);
    fclose(out);

    printf("Done. Saved to %s.\n", argv[2]);

    return(0);
}