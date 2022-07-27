/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package tl.airtoolsgui.model;

import java.io.File;

/**
 *
 * @author lehmann
 */
public class Camera {
    private final String telID;
    private final int flen;
    private final int aperture;
    private final String camera;
    
    public Camera(String telID, int flen, int aperture, String camera) {
        this.telID = telID;
        this.flen = flen;
        this.aperture = aperture;
        this.camera = camera;
    }
    
    public Camera(String telID) {
        this(telID, 0, 0, "");
    }
    
    public String getTelID() {
        return telID;
    }
    
    public String toString() {
        if (this.telID.isBlank() || this.flen==0 || this.aperture==0) return this.telID;
        return this.telID + " (" + this.aperture + "/" + this.flen + ", " + this.camera + ")";
    }
    
    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof Camera)) return false;
        Camera other = (Camera) o;
        return this.telID.equals(other.telID)
                && this.flen == other.flen
                && this.aperture == other.aperture
                && this.camera == other.camera;
    }
}
