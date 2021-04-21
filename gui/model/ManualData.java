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
public class ManualData {
    private final int acor;
    private final int alim;
    private final int dlen;
    private final int dang;
    private final int plen;
    private final int pang;

    public int getAcor() {
        return acor;
    }

    public int getAlim() {
        return alim;
    }

    public int getDlen() {
        return dlen;
    }

    public int getDang() {
        return dang;
    }

    public int getPlen() {
        return plen;
    }

    public int getPang() {
        return pang;
    }
    
    public ManualData (int acor, int alim, int dlen, int dang, int plen, int pang) {
        this.acor = acor;
        this.alim = alim;
        this.dlen = dlen;
        this.dang = dang;
        this.plen = plen;
        this.pang = pang;
    }
}
