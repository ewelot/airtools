/***************************************************************************
 *            functions.c
 *
 *  Wed Feb 22 15:40:44 2006
 *  Copyright  2006  User
 *  Email
 ****************************************************************************/

/*
 *  This program is free software; you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation; either version 2 of the License, or
 *  (at your option) any later version.
 *
 *  This program is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU Library General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with this program; if not, write to the Free Software
 *  Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
 */

#include <math.h>
#include "functions.h"



void bsort (double *x, int n)
{
    int i, j;
    double tmp;

    for (i=n-1; i>0; i--) {
        for (j=0; j<i; j++) {
          if (x[j] > x[j+1]) {
            tmp = x[j];
            x[j] = x[j+1];
            x[j+1] = tmp;
          }
       }
    }
    return;
}

/* reject low/high values from array
 * note: high values are rejected by lowering the array size only */
void clip (double *x, int n, int low, int high)
{
	int i;
	
	if ((low > 0) || (high > 0)) bsort(x, n);
	if (low > 0) {
		for (i=0; i<n-low; i++) {
			x[i] = x[i+low];
		}
	}
	return;
}

double mean (double *x, int n)
{
    int i;
    double ret;
    ret=0;
    for (i=0; i<n; i++) ret += x[i];
    return(ret/(double)n);
}


double median (double *x, int n)
{
    int i;
    double ret;

    bsort(x, n);
    i = (int) floor(n/2.0);
    if (n/2.0 == floor(n/2.0)) {
        ret=(x[i]+x[i-1])/2.0;
    } else {
        ret=x[i];
    }
    return(ret);
}


double stddev (double *x, int n)
{
    int i;
    double m, ret;

    m = mean(x,n);
    ret = 0;
    for (i=0; i<n; i++) ret += (x[i]-m)*(x[i]-m);
    return(sqrt(ret/(double)(n-1)));
}
