/*
 * pnmrowsort.c
 * sort intensities in each row of the image
 * compilation: gcc -lm -lnetpbm -o pnmrowsort pnmrowsort.c
 */

#include <stdio.h>
#include <stdlib.h>
#include <getopt.h>
#include <string.h>    /* strlen, strcpy ... */
#include <strings.h>   /* index */
#include <math.h>
#include <pam.h>
/*#include "pnmccdred.h"*/


static int int_cmp_asc(const void *a, const void *b) {
    const int *ia = (const int *)a; // casting pointer types 
    const int *ib = (const int *)b;
    /* printf("cmp: %d %d  diff=%d\n", a, b, *ia-*ib); */
    return *ia  - *ib; 
	/* integer comparison: returns negative if b > a 
	and positive if a > b */
}

void pnmrowsort(char **inFileName, char **outFileName, 
               int *verbose) {

    struct pam inpam;
    FILE *inFile;
    tuple *inRow;
    int *arr;
    struct pam outpam;
    FILE *outFile;
    tuple *outRow;
    unsigned int row, col, plane;
    unsigned int width, height, planes;

    /* open images */
    inFile = pm_openr(*inFileName);
    if (inFile == NULL) {
        printf("ERROR: cannot open file %s\n", *inFileName);
        exit(-1);
    }
    pnm_readpaminit(inFile, &inpam, sizeof(struct pam));
    outFile = pm_openw(*outFileName);
    if (outFile == NULL) {
        printf("ERROR: cannot open file %s\n", *outFileName);
        exit(-1);
    }
    /* initialization of pam structure is done later on */

    /* if width or height were not specified via command line
     * then take the values from input image */
    width  = inpam.width;
    height = inpam.height;
    planes = inpam.depth;
    if (*verbose > 0)
      printf("  width = %d   height = %d  planes = %d\n", width, height, planes);
    arr = (int *) calloc(width, sizeof(int));

    /* initialize outpam structure */
    outpam = inpam;
    outpam.file   = outFile;
    outpam.width  = width;
    outpam.height = height;
    pnm_writepaminit(&outpam);

    /* allocate tuplerows */
    inRow  = pnm_allocpamrow(&inpam);
    outRow = pnm_allocpamrow(&outpam);

    /* sort pixel by intensity */
    for (row=0; row<height; row++) {
        pnm_readpamrow(&inpam, inRow);
        for (plane=0; plane<planes; plane++) {
            for(col=0; col<width; col++)
                arr[col]=inRow[col][plane];
            qsort(arr, width, sizeof(int), int_cmp_asc);
            if (*verbose > 0) {
                printf("%d %d %d\n", row, col/2, arr[col/2]);
            }
            for (col = 0; col < width; col++)
                outRow[col][plane] = arr[col];
        }
        pnm_writepamrow(&outpam, outRow);
    }

    /* clean up */
    pnm_freepamrow(inRow);
    pnm_freepamrow(outRow);
    pm_close(outFile);
    pm_close(inFile);
    return;
}


int main(int argc, char *argv[])
{
    char *inFileName;
    char *outFileName;
    int opt;
    int nargs, verbose=0;

    /* eliminate some common netpbm options, e.g. -quiet */
    pnm_init(&argc, argv);

    /* read command line short options */
    while((opt = getopt(argc, argv, "uhv")) != -1) {
        switch(opt) {
            case 'u':
            case 'h':
                printf("usage: pnmrowsort [-v] infile outfile\n");
                exit(0);
                break;
            case 'v':
                verbose++;
                break;
            case '?':
                printf("ERROR: unknown option\n");
                exit(-1);
                break;
            default:
                abort();
        }
    }
    
    /* read command line arguments */
    nargs = argc - optind;
    if (nargs != 2) {
        printf("ERROR: missing arguments, try -u switch to show usage info\n");
        exit(-1);
    }

    /* get file names from command line */
    inFileName  = argv[optind];
    outFileName = argv[optind+1];
    
    /* TODO: check all program options and arguments */
    pnmrowsort(&inFileName, &outFileName, &verbose);
    return (0);
}
