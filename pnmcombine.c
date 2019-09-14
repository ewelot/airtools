/*
 * pnmcombine.c
 * compute mean or median or standard deviation for a set of images
 */

/*#define _BSD_SOURCE  rint */

#include <stdio.h>
#include <unistd.h>
#include <getopt.h>
#include <string.h>    /* strlen, strcpy ... */
#include <strings.h>   /* index */
#include <math.h>      /* rint */
#include <pam.h>
#include "functions.h"


enum function {FN_MEAN, FN_MEDIAN, FN_STDDEV};

void pnmcombine (
    enum function function,
    char **painFileName, unsigned int nfiles,
    double *mult, double *add,
    unsigned int lclip, unsigned int hclip,
    unsigned int width, unsigned int height,
    unsigned int left,  unsigned int top,
    char *poutFileName)
{
    FILE **painFile;
    struct pam **inpam;
    struct pam *outpam;
    tuple **tuplerow;
    tuple *outtuplerow;
    unsigned int right, bottom;
    unsigned int row, col, plane, idx, i;

    unsigned int rows=0, cols=0, planes=0;
    double result=0, *x;

    /* allocate arrays */
    x = (double *) calloc(nfiles, sizeof(double));
    painFile = (FILE **) calloc(nfiles, sizeof(FILE*));
    if (painFile == NULL) {
      perror("calloc painFile failed");
    }
    inpam    = (struct pam **) calloc(nfiles, sizeof(struct pam *));
    if (inpam == NULL) {
      perror("calloc inpam failed");
    }
    tuplerow = (tuple **) calloc(nfiles, sizeof(tuple *));
    if (tuplerow == NULL) {
      perror("calloc tuplerow failed");
    }
    for (idx=0; idx<nfiles; idx++) {
      inpam[idx] = (struct pam *) calloc(1, sizeof(struct pam));
      if (inpam[idx] == NULL) {
        perror("calloc inpam[idx] failed");
      }
      /*
      tuplerow[idx] = (tuple *) calloc(1, sizeof(tuple));
      if (tuplerow[idx] == NULL) {
        perror("calloc tuplerow[idx] failed");
      }
      */
    }
    outpam = (struct pam *) calloc(1, sizeof(struct pam));

    /* check pnm headers */
    /* pm_message("check headers ...\n"); */
    for (idx=0; idx<nfiles; idx++) {
        painFile[idx] = pm_openr(painFileName[idx]);
        if (painFile[idx] == NULL)
            pm_error("cannot open file");
        if (idx == 0) {
            pnm_readpaminit(painFile[idx], inpam[idx], sizeof(struct pam));
            rows = inpam[0]->height;
            cols = inpam[0]->width;
            planes = inpam[0]->depth;
        } else {
            pnm_readpaminit(painFile[idx], inpam[idx], sizeof(*(inpam[idx])));
            if (inpam[idx]->height != inpam[0]->height ||
                inpam[idx]->width  != inpam[0]->width  ||
                inpam[idx]->depth  != inpam[0]->depth) {
                pm_message("  %-12s  %dx%d",
                  painFileName[idx], inpam[idx]->width, inpam[idx]->height);
                pm_error("image %d differs from previous ones (size or depth)", idx+1);
            }
        }
        pm_message("  %-12s  %dx%d",
        painFileName[idx], inpam[idx]->width, inpam[idx]->height);
        /* allocate and initialize tuplerows */
        tuplerow[idx] = pnm_allocpamrow(inpam[idx]);
        if (tuplerow[idx] == NULL) {
            perror("calloc tuplerow[idx] failed");
        }
    }

    /* initialize output pam and assoziated tuplerow */
    if (width == 0)  width  = cols - left;
    if (height == 0) height = rows - top;
    right  = left + width - 1;
    bottom = top + height -1;
    *outpam = *inpam[0];
    outpam->file = pm_openw(poutFileName);
    outpam->width = width;
    outpam->height = height;
    pnm_writepaminit(outpam);
    outtuplerow = pnm_allocpamrow(outpam);

    /* apply statistics according to function */
    for (row = 0; row < rows; row++) {
        /* printf("  row = %d\n", row); */
        for (idx=0; idx<nfiles; idx++) {
            pnm_readpamrow(inpam[idx], tuplerow[idx]);
        }
        if (row >= top && row <= bottom) {
            for (col = left; col <= right; col++) {
                for (plane = 0; plane < planes; plane++) {
                    for (idx=0; idx<nfiles; idx++) {
            i = idx + plane*nfiles;
                        x[idx] = mult[i]*tuplerow[idx][col][plane]+add[i];
                    }
                    clip(x, nfiles, lclip, hclip);
                    switch (function) {
                        case FN_MEAN:
                            result = mean(x, nfiles-lclip-hclip);
                            break;
                        case FN_MEDIAN:
                            result = median(x, nfiles-lclip-hclip);
                            break;
                        case FN_STDDEV:
                            result = stddev(x, nfiles-lclip-hclip);
                            break;
                    }
                    if (result < 0) result=0;
                    if (result > outpam->maxval) result=outpam->maxval;
                    outtuplerow[col][plane] = (unsigned int) rint(result);
                }
            }
            pnm_writepamrow(outpam, outtuplerow);
        }
    }

    /* cleaning up */
    for (idx=0; idx<nfiles; idx++) {
        pnm_freepamrow(tuplerow[idx]);
    }
    pnm_freepamrow(outtuplerow);
    for (idx=0; idx<nfiles; idx++) {
      pm_close(painFile[idx]);
    }
    pm_close(outpam->file);

    return;
}


int main(int argc, char *argv[])
{
    enum function function;
    int opt;
    char *clist, *mlist, *alist, *str;
    char **painFileName;
    char *poutFileName;
    double *mult, *add;  /* length: 3*number_of_images */
    unsigned int lclip, hclip, width, height, left, top;
    int i, nargs, nfiles;

    clist = NULL;
    mlist = NULL;
    alist = NULL;
    painFileName = NULL;
    /* eliminate some common netpbm options, e.g. -quiet */
    pnm_init(&argc, argv);

    /* read command line options */
    function = FN_MEAN;
    while((opt = getopt(argc, argv, "udsc:m:a:")) != -1) {
        switch(opt) {
            case 'u':
                printf("usage:\n");
                printf("pnmcombine [-d|s] [-a addR,addG,addB] [-m mulR,mulG,mulB]\n");
                printf("          in1.pnm in2.pnm ... out.pnm\n");
                exit(0);
                break;
            case 'd': function = FN_MEDIAN;
                break;
            case 's': function = FN_STDDEV;
                break;
            case 'c':
				clist=(char *) malloc (strlen(optarg)*sizeof(char));
                strcpy(clist,optarg);
                break;
			case 'a':
				alist=(char *) malloc (strlen(optarg)*sizeof(char));
                strcpy(alist,optarg);
                break;
			case 'm':
				mlist=(char *) malloc (strlen(optarg)*sizeof(char));
                strcpy(mlist,optarg);
                break;
            case '?': pm_error("unknown option %c\n", optopt);
                break;
            default:
                abort();
        }
    }
    nargs = argc - optind;
    if (nargs < 3) {
        printf("ERROR: missing arguments, try -u switch to show usage info\n");
        exit(-1);
    }
    
    /* TODO: handle option "-h" to show usage info */

    /* TODO: handle option "-geometry wxh+x+y" */
    width = 0;
    height = 0;
    left = 0;
    top = 0;

    /* get file names from command line */
    painFileName = (char **) calloc(nargs, sizeof(char *));
    if (painFileName == NULL) {
      perror("calloc painFileName failed");
    }
    for (i=0; i<(nargs-1); i++) {
      painFileName[i]=argv[i+optind];
    }
    poutFileName = argv[i+optind];

    nfiles = i;
    if (nfiles < 1) pm_error("ERROR: no input files specified.");
    pm_message("  nfiles = %d", nfiles);
	
	/* read lclip,hclip from string clist, if specified */
    lclip = 0;
    hclip = 0;
	if (clist != NULL) {
		str=clist;
		hclip=atoi(str);
		if((str=index(str, ',')) != NULL) {
			++str;
			lclip=atoi(str);
		}
	}
	
    /* extract mult and add from mlist and alist */
    mult=(double *) malloc (nfiles*3*sizeof(double));
    for (i=0; i<3*nfiles; i++) {mult[i]=1;}
    if (mlist != NULL) {
      str=mlist;
      mult[0]=atof(str);
      for (i=1; i<3*nfiles; i++) {
        if((str=index(str, ',')) == NULL) {break;}
        ++str;
        mult[i]=atof(str);
      }
      if (i != 3*nfiles) {
        pm_error("-m has wrong number of comma separated values");
      }
    }

    add=(double *) malloc (nfiles*3*sizeof(double));
    for (i=0; i<3*nfiles; i++) {add[i]=0;}
    if (alist != NULL) {
      str=alist;
      add[0]=atof(str);
      for (i=1; i<3*nfiles; i++) {
        if((str=index(str, ',')) == NULL) {break;}
        ++str;
        add[i]=atof(str);
      }
      if (i != 3*nfiles) {
        pm_error("-a has wrong number of comma separated values");
      }
    }

    pnmcombine(function, painFileName, nfiles,
      mult, add, lclip, hclip, width, height, left, top,
      poutFileName);

    return (0);
}
