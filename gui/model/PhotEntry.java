/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package tl.airtoolsgui.model;

/**
 *
 * @author lehmann
 */
public class PhotEntry {
    // Photometry entry in image header file containing parameters used
    // by AIphotcal
    private final int id;
    private final int aidx;
    private final String pcat;

    private final String pcol;
    private final String cind;
    private final double arad;
    private final int nmax;     // max number of stars
    private final double rlim;  // mag limit
    private final int rmax;     // max search radius

    public String getPcol() {
        return pcol;
    }

    public String getCind() {
        return cind;
    }

    public double getArad() {
        return arad;
    }

    public int getNmax() {
        return nmax;
    }

    public double getRlim() {
        return rlim;
    }

    public int getRmax() {
        return rmax;
    }

    public PhotEntry (int id, int aidx, String pcat, String pcol,
            String cind, double arad, int nmax, double rlim, int rmax) {
        this.id = id;
        this.aidx = aidx;
        this.pcat = pcat;
        this.pcol = pcol;
        this.cind = cind;
        this.arad = arad;
        this.nmax = nmax;
        this.rlim = rlim;
        this.rmax = rmax;
    }

    public PhotEntry (int aidx, String pcat) {
        //this.PhotEntry (id, aidx, pcat, "", "", 0.0, 0, 0.0, 0);
        this.id = -1;
        this.aidx = aidx;
        this.pcat = pcat;
        this.pcol = "";
        this.cind = "";
        this.arad = 0;
        this.nmax = 0;
        this.rlim = 0;
        this.rmax = 0;
    }

    public boolean equals (PhotEntry other) {
        // key is made of aidx + pcat
        return other.aidx == this.aidx && other.pcat.equalsIgnoreCase(this.pcat);
    }

    public String show() {
        // show key and some data values
        return "PhotEntry id=" + id + ": " + aidx + " " + pcat + " " + pcol + " " + cind + " " + " ap=" + arad;
    }
    
    @Override
    public String toString() {
        return "PhotEntry id=" + id + ": band=" + aidx + " catalog=" + pcat;
    }

}
    
