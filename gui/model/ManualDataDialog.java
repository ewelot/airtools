/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package tl.airtoolsgui.model;

import tl.airtoolsgui.controller.ManualDataController;

/**
 * FXML Controller class
 *
 * @author lehmann
 */
public class ManualDataDialog extends CometPhotometryDialog {
    private final ManualDataController controller;

    public ManualDataDialog(String fxml, String title) {
        super(fxml, title);
        controller = (ManualDataController) getController();
    }

    @Override
    public void setImageSet(ImageSet imgSet) {
        super.setImageSet(imgSet);
        controller.setImageSet(imgSet);
    }
    
    public String[] getValues() {
        return controller.getValues();
    }
}
