/*
 * pnmtomef.c
 * convert pnm image to signed 16-bit multi-extension FITS format
 */

#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <math.h>
#include <pnm.h>

#define write_card(s)    fwrite( s, sizeof(char), 80, stdout )


int
main( argc, argv )
    int argc;
    char* argv[];
{
    FILE* ifp;
    xel** xels;
    xel* xelrow;
    register xel* xP;
    int argn, row, col, rows, cols, planes, format, i, npad, bitpix;
    double datamin, datamax, bscale, fits_bzero;
    xelval maxval;
    register unsigned short color;
    char card[81];
    char* usage = "[pnmfile]";

    pnm_init( &argc, argv );

    argn = 1;
    while ( argn < argc && argv[argn][0] == '-' && argv[argn][1] != '\0' )
        {
          pm_usage( usage );
          ++argn;
        }
    if ( argn != argc )
        {
        ifp = pm_openr( argv[argn] );
        ++argn;
        }
    else
        ifp = stdin;

    if ( argn != argc )
        pm_usage( usage );

    xels = pnm_readpnm( ifp, &cols, &rows, &maxval, &format );

    datamin = 0.0;
    datamax = (double) maxval;
    fits_bzero = datamin;
    bscale = ( datamax - datamin ) / ( double ) maxval;

    bitpix = 8;
    if (maxval > 255) {
      bitpix = 16;
      fits_bzero = 32768;
    }

    pm_close( ifp );

    /* Figure out the proper depth */
    switch ( PNM_FORMAT_TYPE(format) )
        {
        case PPM_TYPE:
        planes = 3;
        break;

        default:
        planes = 1;
        break;
        }

    /* write out primary image fits header */
    i = 0;
    sprintf( card, "SIMPLE  =                    T%50s", "" );
    write_card( card ); ++i;
    sprintf( card, "BITPIX  =           %10d%50s", bitpix, "" );
    write_card( card ); ++i;
    sprintf( card, "NAXIS   =           %10d%50s", 2, "" );
    write_card( card ); ++i;
    sprintf( card, "NAXIS1  =           %10d%50s", cols, "" );
    write_card( card ); ++i;
    sprintf( card, "NAXIS2  =           %10d%50s", rows, "" );
    write_card( card ); ++i;
    if ( planes == 3 ) {
      sprintf( card, "EXTEND  =                    T%50s", "" );
      write_card( card ); ++i;
      sprintf( card, "FILTER  = 'R'                 %50s", "" );
      write_card( card ); ++i;
    }
    sprintf( card, "BSCALE  =         %E%50s", bscale, "" );
    write_card( card ); ++i;
    sprintf( card, "BZERO   =         %E%50s", fits_bzero, "" );
    write_card( card ); ++i;
    sprintf( card, "DATAMAX =         %E%50s", datamax, "" );
    write_card( card ); ++i;
    sprintf( card, "DATAMIN =         %E%50s", datamin, "" );
    write_card( card ); ++i;
    sprintf( card, "%-80s", "HISTORY Created by pnmtomef." );
    write_card( card ); ++i;
    sprintf( card, "%-80s", "END" );
    write_card( card ); ++i;

    /* pad end of primary image header with blanks */
    npad = ( i * 80 ) % 2880;
    if ( npad == 0 )
        npad = 2880;
    while ( npad++ < 2880 )
        putchar ( ' ' );

    /* copy first image plane (red channel in case of RGB PPM image) */
    for ( row = rows-1; row >= 0; row-- ) {
      xelrow = xels[row];
      for ( col = 0, xP = xelrow; col < cols; ++col, ++xP ) {
        if ( planes == 3 )
            color = PPM_GETR( *xP );
        else
            color = PNM_GET1( *xP );
        color = color - fits_bzero;
        if ( bitpix == 16 )
            putchar( ( color >> 8 ) & 0xff );

        putchar( color & 0xff );
      }
    }

    /* pad end of data records with nulls */
    npad = ( rows * cols * bitpix / 8 ) % 2880;
    if ( npad == 0 )
        npad = 2880;
    while ( npad++ < 2880 )
        putchar ( 0 );

    if ( planes == 3 ) {
      /* write out first extension fits header */
      i = 0;
      sprintf( card, "XTENSION= 'IMAGE   '          %50s", "" );
      write_card( card ); ++i;
      sprintf( card, "BITPIX  =           %10d%50s", bitpix, "" );
      write_card( card ); ++i;
      sprintf( card, "NAXIS   =           %10d%50s", 2, "" );
      write_card( card ); ++i;
      sprintf( card, "NAXIS1  =           %10d%50s", cols, "" );
      write_card( card ); ++i;
      sprintf( card, "NAXIS2  =           %10d%50s", rows, "" );
      write_card( card ); ++i;
      sprintf( card, "PCOUNT  =           %10d%50s", 0, "" );
      write_card( card ); ++i;
      sprintf( card, "GCOUNT  =           %10d%50s", 1, "" );
      write_card( card ); ++i;
      sprintf( card, "FILTER  = 'G'                 %50s", "" );
      write_card( card ); ++i;
      sprintf( card, "BSCALE  =         %E%50s", bscale, "" );
      write_card( card ); ++i;
      sprintf( card, "BZERO   =         %E%50s", fits_bzero, "" );
      write_card( card ); ++i;
      sprintf( card, "DATAMAX =         %E%50s", datamax, "" );
      write_card( card ); ++i;
      sprintf( card, "DATAMIN =         %E%50s", datamin, "" );
      write_card( card ); ++i;
      sprintf( card, "%-80s", "HISTORY Created by pnmtomef." );
      write_card( card ); ++i;
      sprintf( card, "%-80s", "END" );
      write_card( card ); ++i;

      /* pad end of first extension header with blanks */
      npad = ( i * 80 ) % 2880;
      if ( npad == 0 )
          npad = 2880;
      while ( npad++ < 2880 )
          putchar ( ' ' );

      /* copy second image plane (green channel in case of RGB PPM image) */
      for ( row = rows-1; row >= 0; row-- ) {
        xelrow = xels[row];
        for ( col = 0, xP = xelrow; col < cols; ++col, ++xP ) {
          color = PPM_GETG( *xP );
          color = color - fits_bzero;
          if ( bitpix == 16 )
            putchar( ( color >> 8 ) & 0xff );

          putchar( color & 0xff );
        }
      }

      /* pad end of data records with nulls */
      npad = ( rows * cols * bitpix / 8 ) % 2880;
      if ( npad == 0 )
          npad = 2880;
      while ( npad++ < 2880 )
          putchar ( 0 );

      /* write out second extension fits header */
      i = 0;
      sprintf( card, "XTENSION= 'IMAGE   '          %50s", "" );
      write_card( card ); ++i;
      sprintf( card, "BITPIX  =           %10d%50s", bitpix, "" );
      write_card( card ); ++i;
      sprintf( card, "NAXIS   =           %10d%50s", 2, "" );
      write_card( card ); ++i;
      sprintf( card, "NAXIS1  =           %10d%50s", cols, "" );
      write_card( card ); ++i;
      sprintf( card, "NAXIS2  =           %10d%50s", rows, "" );
      write_card( card ); ++i;
      sprintf( card, "PCOUNT  =           %10d%50s", 0, "" );
      write_card( card ); ++i;
      sprintf( card, "GCOUNT  =           %10d%50s", 1, "" );
      write_card( card ); ++i;
      sprintf( card, "FILTER  = 'B'                 %50s", "" );
      write_card( card ); ++i;
      sprintf( card, "BSCALE  =         %E%50s", bscale, "" );
      write_card( card ); ++i;
      sprintf( card, "BZERO   =         %E%50s", fits_bzero, "" );
      write_card( card ); ++i;
      sprintf( card, "DATAMAX =         %E%50s", datamax, "" );
      write_card( card ); ++i;
      sprintf( card, "DATAMIN =         %E%50s", datamin, "" );
      write_card( card ); ++i;
      sprintf( card, "%-80s", "HISTORY Created by pnmtomef." );
      write_card( card ); ++i;
      sprintf( card, "%-80s", "END" );
      write_card( card ); ++i;

      /* pad end of second extension header with blanks */
      npad = ( i * 80 ) % 2880;
      if ( npad == 0 )
          npad = 2880;
      while ( npad++ < 2880 )
          putchar ( ' ' );

      /* copy third image plane (blue channel in case of RGB PPM image) */
      for ( row = rows-1; row >= 0; row-- ) {
        xelrow = xels[row];
        for ( col = 0, xP = xelrow; col < cols; ++col, ++xP ) {
          color = PPM_GETB( *xP );
          color = color - fits_bzero;
          if ( bitpix == 16 )
            putchar( ( color >> 8 ) & 0xff );

          putchar( color & 0xff );
        }
      }

      /* pad end of data records with nulls */
      npad = ( rows * cols * bitpix / 8 ) % 2880;
      if ( npad == 0 )
          npad = 2880;
      while ( npad++ < 2880 )
          putchar ( 0 );
    }

    exit( 0 );
}
