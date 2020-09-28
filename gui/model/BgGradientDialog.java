/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package tl.airtoolsgui.model;

import tl.airtoolsgui.controller.BgGradientController;

/**
 * FXML Controller class
 *
 * @author lehmann
 */
public class BgGradientDialog extends CometPhotometryDialog {
    private BgGradientController controller;

    public BgGradientDialog(String fxml, String title) {
        super(fxml, title);
        controller = (BgGradientController) getController();
    }

    public void setImageSet(ImageSet imgSet) {
        super.setImageSet(imgSet);
        controller.setImageSet(imgSet);
    }
    
    public String[] getValues() {
        return controller.getValues();
    }
    
    public void setValues(String[] sarray) {
        controller.setValues(sarray);
    }

}
