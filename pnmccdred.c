/*
 * pnmccdred.c
 * process astronomical raw CCD image:
 *   subtract dark image,
 *   divide by flatfield image,
 *   scale intensities in each color band,
 *   add offsets for each color band,
 *   change image size (new pixels are assigned background intensity)
 */

#include <stdio.h>
#include <stdlib.h>
#include <getopt.h>
#include <string.h>    /* strlen, strcpy ... */
#include <strings.h>   /* index */
#include <math.h>
#include <pam.h>
/*#include "pnmccdred.h"*/


void pnmccdred(char **inFileName, char **outFileName, 
               char **dkFileName, char **ffFileName,
               double *mult, double *add,
               unsigned int *width, unsigned int *height, double *bg,
	       int *verbose) {

    struct pam inpam, dkpam, ffpam;
    FILE *inFile, *dkFile=NULL, *ffFile=NULL;
    tuple *inRow, *dkRow=NULL, *ffRow=NULL;
    struct pam outpam;
    FILE *outFile;
    tuple *outRow;
    unsigned int row, col, plane;
    unsigned int rmargin, cmargin, rskip, cskip;
    int i, idx;
    double result;

    /* show some parameters */
    if (*verbose > 0) {
	for (i=1;i<3;i++) {
	    printf("%d  m=%.2f  a=%.2f\n", i, mult[i], add[i]);
        }
    }

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

    if (*dkFileName != NULL) {
        dkFile = pm_openr(*dkFileName);
        if (dkFile == NULL) {
            printf("ERROR: cannot open file %s\n", *dkFileName);
            exit(-1);
        }
        pnm_readpaminit(dkFile, &dkpam, sizeof(struct pam));
    }
    if (*ffFileName != NULL) {
        ffFile = pm_openr(*ffFileName);
        if (ffFile == NULL) {
            printf("ERROR: cannot open file %s\n", *ffFileName);
            exit(-1);
        }
        pnm_readpaminit(ffFile, &ffpam, sizeof(struct pam));
    }

    /* if width or height were not specified via command line
     * then take the values from input image */
    if (*width == 0) *width  = inpam.width;
    if (*height == 0) *height = inpam.height;
    if (*verbose > 0)
      printf("  new width = %d   new height = %d\n", *width, *height);

    /* initialize outpam structure */
    outpam = inpam;
    outpam.file   = outFile;
    outpam.width  = *width;
    outpam.height = *height;
    pnm_writepaminit(&outpam);

    /* determine number of rows, columns to discard from input image */
    rskip = 0;
    cskip = 0;
    if (outpam.height < inpam.height) rskip = (inpam.height-outpam.height)/2;
    if (outpam.width  < inpam.width)  cskip = (inpam.width-outpam.width)/2;
    if (*verbose > 0)
      printf("  rskip=%d   cskip=%d\n", rskip, cskip);

    /* determine number of background rows, columns to add to output image */
    rmargin = 0;
    cmargin = 0;
    if (outpam.height > inpam.height) rmargin = (outpam.height-inpam.height)/2;
    if (outpam.width  > inpam.width)  cmargin = (outpam.width-inpam.width)/2;
    if (*verbose > 0)
      printf("  rmargin=%d   cmargin=%d\n", rmargin, cmargin);

    /* allocate tuplerows */
    inRow  = pnm_allocpamrow(&inpam);
    outRow = pnm_allocpamrow(&outpam);
    if (*dkFileName != NULL) dkRow  = pnm_allocpamrow(&dkpam);
    if (*ffFileName != NULL) ffRow  = pnm_allocpamrow(&ffpam);

    /* apply ccd reduction algorithm */
    for (i = 0; i < rskip; i++) {
        pnm_readpamrow(&inpam, inRow);
        if (*dkFileName != NULL) pnm_readpamrow(&dkpam, dkRow);
        if (*ffFileName != NULL) pnm_readpamrow(&ffpam, ffRow);
    }
    for (row = 0; row < outpam.height; row++) {
        if ((row < rmargin) || (row >= rmargin+inpam.height)) {
            for (col = 0; col < outpam.width; col++) {
                for (plane = 0; plane < outpam.depth; plane++) {
                  outRow[col][plane] = *bg;
                }
            }
        } else {
            pnm_readpamrow(&inpam, inRow);
            if (*dkFileName != NULL) pnm_readpamrow(&dkpam, dkRow);
            if (*ffFileName != NULL) pnm_readpamrow(&ffpam, ffRow);
            for (col = 0; col < outpam.width; col++) {
                if ((col < cmargin) || (col >= cmargin+inpam.width)) {
                    for (plane = 0; plane < outpam.depth; plane++) {
                      outRow[col][plane] = *bg;
                    }
                } else {
                    idx = col+cskip-cmargin;
                    for (plane = 0; plane < outpam.depth; plane++) {
                      result = inRow[idx][plane];
                      if (*dkFileName != NULL)
                        result = result - (double) dkRow[idx][plane];
                      if (*ffFileName != NULL)
                        result = result / (double) ffRow[idx][plane];
                      result = floor(mult[plane] * result + add[plane] + 0.5);
                      if (result > outpam.maxval) result = outpam.maxval;
                      if (result < 0) result = 0;
                      outRow[col][plane] = (int) result;
                    }
                }
            }
        }
        pnm_writepamrow(&outpam, outRow);
    }
    for (i = rskip+outpam.height; i < inpam.height; i++) {
        pnm_readpamrow(&inpam, inRow);
        if (*dkFileName != NULL) pnm_readpamrow(&dkpam, dkRow);
        if (*ffFileName != NULL) pnm_readpamrow(&ffpam, ffRow);
    }

    /* clean up */
    pnm_freepamrow(inRow);
    pnm_freepamrow(outRow);
    if (*dkFileName != NULL) {pnm_freepamrow(dkRow); pm_close(dkFile);}
    if (*ffFileName != NULL) {pnm_freepamrow(ffRow); pm_close(ffFile);}
    pm_close(outFile);
    pm_close(inFile);
    return;
}


int ato3f (char *s, double *d) {
    /* read 3 doubles from comma separated string */
    char *str;

    /* split string */
    d[0]=atof(s);
    if((str=index(s, ',')) == NULL) {return(-1);}
    ++str;
    d[1]=atof(str);
    if((str=index(str, ',')) == NULL) {return(-1);}
    ++str;
    d[2]=atof(str);
    return(0);
}


int main(int argc, char *argv[])
{
    char *inFileName, *dkFileName, *skFileName;
    char *outFileName;
    double bg, mult[3], add[3];
    int opt;
    unsigned int width, height;
    int i, nargs, verbose, err;

    /* eliminate some common netpbm options, e.g. -quiet */
    pnm_init(&argc, argv);

    /* initialize some variables */
    width=0; height=0;
    dkFileName=NULL; skFileName=NULL;
    bg=0; for (i=0;i<3;i++) {mult[i]=1; add[i]=0;} verbose=0;

    /* read command line short options */
    while((opt = getopt(argc, argv, "uvm:a:b:w:h:d:s:")) != -1) {
        switch(opt) {
            case 'u':
                printf("usage:\n");
                printf("pnmccdred [-d darkim] [-s flatim]\n");
                printf("          [-a addR,addG,addB] [-m mulR,mulG,mulB]\n");
                printf("          [-w width] [-h height] [-b bg]\n");
                printf("          in.pnm out.pnm\n");
                exit(0);
                break;
            case 'v':
                verbose++;
                break;
            case 'd':
                dkFileName=optarg;
                break;
            case 's':
                skFileName=optarg;
                break;
            case 'm':
                if((err=ato3f(optarg, mult)) < 0) {
                    mult[0]=mult[1]=mult[2]=atof(optarg);
                }
                break;
            case 'a':
                if((err=ato3f(optarg, add)) < 0) {
                    add[0]=add[1]=add[2]=atof(optarg);
                }
                break;
            case 'w':
                width=atoi(optarg);
                break;
            case 'h':
                height=atoi(optarg);
                break;
            case 'b':
                bg=atof(optarg);
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
    /*
    inFileName  = (char *) malloc(strlen(argv[optind]) * sizeof(char));
    strcpy(inFileName, argv[optind]);
    outFileName = (char *) malloc(strlen(argv[optind+1]) * sizeof(char));
    strcpy(outFileName, argv[optind+1]);
    */
    inFileName  = argv[optind];
    outFileName = argv[optind+1];
    
    /* TODO: check all program options and arguments */
    if (verbose > 0)
        printf("  m=%.2f %.2f %.2f  a=%.2f %.2f %.2f  bg=%.2f\n",
               mult[0], mult[1], mult[2], add[0], add[1], add[2], bg);
    pnmccdred(&inFileName, &outFileName, &dkFileName, &skFileName,
              &mult[0], &add[0], &width, &height, &bg, &verbose);
    return (0);
}
