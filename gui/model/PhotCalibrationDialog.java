/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package tl.airtoolsgui.model;

import tl.airtoolsgui.controller.PhotCalibrationController;

/**
 * FXML Controller class
 *
 * @author lehmann
 */
public class PhotCalibrationDialog extends CometPhotometryDialog {
    private final PhotCalibrationController controller;

    public PhotCalibrationDialog(String fxml, String title) {
        super(fxml, title);
        controller = (PhotCalibrationController) getController();
    }

    @Override
    public void setImageSet(ImageSet imgSet) {
        super.setImageSet(imgSet);
        controller.setImageSet(imgSet);
    }
    
    public boolean isOverwrite() {
        return controller.getOverwrite();
    }
    
    public String[] getValues() {
        return controller.getValues();
    }
}
