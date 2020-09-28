/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package tl.airtoolsgui.model;

import tl.airtoolsgui.controller.CometExtractController;

/**
 * FXML Controller class
 *
 * @author lehmann
 */
public class CometExtractDialog extends CometPhotometryDialog {
    private CometExtractController controller;

    public CometExtractDialog(String fxml, String title) {
        super(fxml, title);
        controller = (CometExtractController) getController();
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
