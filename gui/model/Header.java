/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package tl.airtoolsgui.model;

import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.Properties;

/**
 *
 * @author lehmann
 */
public class Header {
    
    private static Properties prop;
    public List<ManualData> manualDataList;
    public List<PhotEntry> photEntryList;
    
    public Header(String path) throws FileNotFoundException, IOException {
        Header.prop = new Properties();
        manualDataList = new ArrayList<>();
        photEntryList = new ArrayList<>();
        String str;
        String undefNumber = "-1";
        String undefString = "";
        int i;
        
        // keywords related to manual data measurements
        int acor=0;
        int alim=0;
        int dlen;
        int dang;
        int plen;
        int pang;
        String comment;
        
        // keywords related to photometry
        int aidx;
        String pcat;
        String pcol;
        String cind;
        double arad;
        int nmax;
        double rlim;
        int rmax;
        
        prop.load(new FileInputStream(path));
        
        // read entries of manual measurements from header (always 3, one for each channel)
        // TODO: handle possible NumberFormatException in Integer.valueOf(str)
        for (i=1; i<=3; i++) {
            str=prop.getProperty("AI_ACOR" + i, undefNumber).replaceAll("/.*", "").strip().replaceAll("'", "");
            if (! str.isBlank()) acor=Integer.valueOf(str); else acor=Integer.valueOf(undefNumber);
            str=prop.getProperty("AI_ALIM" + i, undefNumber).replaceAll("/.*", "").strip().replaceAll("'", "");
            if (! str.isBlank()) alim=Integer.valueOf(str); else alim=Integer.valueOf(undefNumber);

            str=prop.getProperty("AI_DLEN", undefNumber).replaceAll("/.*", "").strip().replaceAll("'", "");
            if (! str.isBlank()) dlen=Integer.valueOf(str); else dlen=Integer.valueOf(undefNumber);
            str=prop.getProperty("AI_DANG", undefNumber).replaceAll("/.*", "").strip().replaceAll("'", "");
            if (! str.isBlank()) dang=Integer.valueOf(str); else dang=Integer.valueOf(undefNumber);
            str=prop.getProperty("AI_PLEN", undefNumber).replaceAll("/.*", "").strip().replaceAll("'", "");
            if (! str.isBlank()) plen=Integer.valueOf(str); else plen=Integer.valueOf(undefNumber);
            str=prop.getProperty("AI_PANG", undefNumber).replaceAll("/.*", "").strip().replaceAll("'", "");
            if (! str.isBlank()) pang=Integer.valueOf(str); else pang=Integer.valueOf(undefNumber);
            comment=prop.getProperty("AI_COMM", undefString).replaceAll("/.*", "").strip().replaceAll("'", "");

            manualDataList.add(new ManualData(acor, alim, dlen, dang, plen, pang, comment));
        }

        
        // read photometry entries from header (max 9, one for each channel+catalog)
        for (i=1; i<=9; i++) {
            if (prop.getProperty("AP_PCAT" + i) != null) {
                str=prop.getProperty("AP_AIDX" + i).replaceAll("/.*", "").strip().replaceAll("'", "");
                aidx=Integer.valueOf(str);
                pcat=prop.getProperty("AP_PCAT" + i).replaceAll("/.*", "").strip().replaceAll("'", "");
                
                // optional data
                pcol=prop.getProperty("AP_PCOL" + i).replaceAll("/.*", "").strip().replaceAll("'", "");
                cind=prop.getProperty("AP_CIND" + i, undefString).replaceAll("/.*", "").strip().replaceAll("'", "");
                str=prop.getProperty("AP_ARAD" + i, undefNumber).replaceAll("/.*", "").strip().replaceAll("'", "");
                arad=Double.valueOf(str);
                str=prop.getProperty("AP_NMAX" + i, undefNumber).replaceAll("/.*", "").strip().replaceAll("'", "");
                nmax=Integer.valueOf(str);
                str=prop.getProperty("AP_RLIM" + i, undefNumber).replaceAll("/.*", "").strip().replaceAll("'", "");
                rlim=Double.valueOf(str);
                str=prop.getProperty("AP_RMAX" + i, undefNumber).replaceAll("/.*", "").strip().replaceAll("'", "");
                rmax=Integer.valueOf(str);
                
                photEntryList.add(new PhotEntry(i, aidx, pcat, pcol, cind, arad, nmax, rlim, rmax));
            }
        }
        
        // show all entries
        System.out.println("Header successfully read:");
        System.out.println("photEntryList = " + photEntryList);
    }
    
    public ManualData getManualData (int imagePlane) {
        return manualDataList.get(imagePlane - 1);
    }
    
    public PhotEntry getPhotEntry (int imagePlane, String catalog) {
        PhotEntry needleEntry = new PhotEntry(imagePlane, catalog);
        for (PhotEntry stackEntry: photEntryList) {
            if (stackEntry.equals(needleEntry)) {
                return stackEntry;
            }
        }
        return null;
    }
    
    public boolean isColor () {
        String str;
        String default_str = "1";
        int num_bands;

        str=prop.getProperty("NAXIS3", default_str).replaceAll("/.*", "").strip().replaceAll("'", "");
        num_bands=Integer.parseInt(str);
        return num_bands == 3;
    }
}