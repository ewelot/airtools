/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package tl.airtoolsgui.model;

import java.io.File;
import java.io.IOException;
import java.util.logging.Level;
import java.util.logging.Logger;

import nom.tam.fits.Fits;
import nom.tam.fits.FitsException;
import nom.tam.fits.Header;


/**
 *
 * @author lehmann
 */
public class ImageSet {
    private final String projectDir;
    private final String setname;
    private final String target;
    private final int type;   // -1: dummy, 0: undef, 1: light, 2: bias, 3: dark, 4: flat

    public ImageSet(String projectDir, String setname, String target, int type) {
        this.projectDir = projectDir;
        this.setname = setname;
        this.target = target;
        this.type = type;
    }
    
    public String getProjectDir() {
        return projectDir;
    }
    
    public String getSetname() {
        return setname;
    }
    
    public String getStarStack() {
        // note: prefering ppm over pgm
        //  returns relative path to projectDir
        String fname;
        File f;
        fname = setname + ".fits";
        f = new File(projectDir + "/" + fname);
        if (f.exists() && f.isFile()) {
            return fname;
        } else {
            fname = setname + ".ppm";
            f = new File(projectDir + "/" + fname);
            if (f.exists() && f.isFile()) {
                return fname;
            } else {
                fname = setname + ".pgm";
                f = new File(projectDir + "/" + fname);
                if (f.exists() && f.isFile()) return fname;
            }
        }
        
        // no file found
        return "";
    }

    public boolean isColor() {
        String fname;

        fname = getStarStack();
        if (fname.isEmpty()) {
            System.out.println("ERROR: isColor(): unable to find star stack image.");
            return false;
        }
        if (fname.endsWith(".ppm")) return true;
        if (fname.endsWith(".pgm")) return false;
        if (fname.endsWith(".fits")) {
            try {        
                Fits f = new Fits(projectDir + "/" + fname);
                Header header = f.getHDU(0).getHeader();
                int naxis3 =  header.getIntValue("NAXIS3");
                boolean isColor = naxis3 == 3;
                System.out.println("ImageSet.isColor = " + isColor);
                return isColor;
            } catch (FitsException ex1) {
                Logger.getLogger(ImageSet.class.getName()).log(Level.SEVERE, null, ex1);
                System.out.println("ERROR: file " + fname + " is not a valid FITS file.");
            } catch (IOException ex2) {
                Logger.getLogger(ImageSet.class.getName()).log(Level.SEVERE, null, ex2);
                System.out.println("ERROR: file " + fname + " cannot be read (no FITS header?).");
            }
        }
        System.out.println("WARNING: isColor(): file " + fname + " has unsupported format.");
        return false;
    }
    
    public String getHeader() {
        //  returns relative path to projectDir
        String fname;
        File f;
        fname = setname + ".head";
        f = new File(projectDir + "/" + fname);
        if (f.exists() && f.isFile()) {
            return fname;
        }
        
        // no file found
        return "";
    }
    
    
    public boolean isLight() {
        if (type == 1) {
            return true;
        } else {
            return false;
        }
    }

    public String toString() {
        return this.setname + " (" + this.target + ")";
    }
    
    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof ImageSet)) return false;
        ImageSet other = (ImageSet) o;
        return this.projectDir.equals(other.projectDir)
                && this.setname.equals(other.setname)
                && this.target.equals(other.target)
                && this.type == other.type;
    }
}
