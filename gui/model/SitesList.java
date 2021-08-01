/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package tl.airtoolsgui.model;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.Scanner;
import java.util.logging.Level;
import java.util.logging.Logger;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import tl.airtoolsgui.controller.CometPhotometryController;

/**
 *
 * @author lehmann
 */
public class SitesList {
    private List<String> siteNames = new ArrayList<>();

    public SitesList(File sitesFile, SimpleLogger logger) {
        BufferedReader inFile = null;
        try {
            inFile = new BufferedReader(new FileReader(sitesFile));
        } catch (IOException ex) {
            // Logger.getLogger(CometPhotometryController.class.getName()).log(Level.SEVERE, null, ex);
            logger.log("ERROR: IOException when trying to read sites file");
        }

        // extract site names from column "location"
        String line;
        //Pattern regexp =   Pattern.compile("^[A-Z][a-zA-Z0-9]+[ ]+[a-zA-Z0-9]+[ ]+[+-]{0,1}[0-9.,]+[ ]+[+-]{0,1}[0-9.,]+[ ]+");
        Pattern regexp =   Pattern.compile("^[A-Z][a-zA-Z0-9]+[ ]+");
        Matcher matcher = regexp.matcher("");
        try {
            boolean foundHeader = false;
            int colNum=-1;
            while (( line = inFile.readLine()) != null){
                // first line starting with # is header
                if (! foundHeader && line.startsWith("#")) {
                    foundHeader = true;
                    String colName;
                    Scanner sc = new Scanner(line);
                    int i=0;
                    while (sc.hasNext()) {
                        colName=sc.next();
                        if (colName.equalsIgnoreCase("location")) {
                            colNum = i-1;
                            //System.out.println("found column \"location\" at position " + colNum);
                            break;
                        }
                        i++;
                    }
                }
                if (colNum < 0 || line.startsWith("#")) continue;
                matcher.reset(line);
                if (matcher.find()) {
                    String[] columns = line.split("[ ]+");
                    if (columns.length >= 5) {
                        siteNames.add(columns[colNum]);
                    }
                }
            }
            if (colNum < 0) {
                System.out.println("ERROR: cannot get sites, column \"location\" not found");
                logger.log("ERROR: cannot get sites, column \"location\" not found");
            }
        } catch (IOException ex) {
            Logger.getLogger(CometPhotometryController.class.getName()).log(Level.SEVERE, null, ex);
        } finally {
            try {
                inFile.close();
            } catch (IOException ex) {
                Logger.getLogger(CometPhotometryController.class.getName()).log(Level.SEVERE, null, ex);
            }
        }
    }

    public List<String> getSiteNames() {
        return siteNames;
    }

    public boolean isEmpty() {
        return siteNames.isEmpty();
    }
    
    public boolean contains(String siteName) {
        return siteNames.contains(siteName);
    }
}
