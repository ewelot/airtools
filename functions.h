/***************************************************************************
 *            functions.h
 *
 *  Wed Feb 22 15:40:20 2006
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
 
#ifndef _FUNCTIONS_H
#define _FUNCTIONS_H

#ifdef __cplusplus
extern "C"
{
#endif


void bsort (double *x, int n);
void clip (double *x, int n, int low, int high);
double mean (double *x, int n);
double median (double *x, int n);
double stddev (double *x, int n);



#ifdef __cplusplus
}
#endif

#endif /* _FUNCTIONS_H */
