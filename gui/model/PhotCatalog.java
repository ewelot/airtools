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
public class PhotCatalog {
    private final String id;
    private final String name;
    private final String[] colorFit;   // color fit functions
    private final String defaultVFit;  // default function to fit V color
    
    public PhotCatalog (String id, String name, String[] colorFit, String defaultVFit) {
        this.id = id;
        this.name = name;
        this.colorFit = colorFit;
        this.defaultVFit = defaultVFit;
    }

    public String getId() {
        return id;
    }

    public String getName() {
        return name;
    }

    public String[] getColorFit() {
        return colorFit;
    }

    public String getDefaultVFit() {
        return defaultVFit;
    }

    @Override
    public String toString() {
        return getName();
    }
}
