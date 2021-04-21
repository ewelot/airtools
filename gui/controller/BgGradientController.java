/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package tl.airtoolsgui.controller;

import java.io.File;
import java.net.URL;
import java.util.ResourceBundle;
import javafx.fxml.FXML;
import javafx.fxml.Initializable;
import javafx.scene.control.CheckBox;
import javafx.scene.control.ComboBox;
import javafx.scene.control.DialogPane;
import javafx.scene.control.Label;
import javafx.scene.control.RadioButton;
import javafx.scene.control.TextField;
import javafx.scene.control.ToggleGroup;
import tl.airtoolsgui.model.ImageSet;

/**
 * FXML Controller class
 *
 * @author lehmann
 */
public class BgGradientController implements Initializable {

    @FXML
    private DialogPane paramDialogPane;
    @FXML
    private Label labelWarning;
    @FXML
    private TextField tfImageSet;
    @FXML
    private ComboBox<String> cbBgModel;
    @FXML
    private ComboBox<String> cbBgMult;
    @FXML
    private ToggleGroup badRegionGroup;
    @FXML
    private RadioButton rbBadFrame;
    @FXML
    private RadioButton rbBadFile;

    private ImageSet imgSet;
    
    /**
     * Initializes the controller class.
     */
    @Override
    public void initialize(URL url, ResourceBundle rb) {
        labelWarning.setText("");
        cbBgModel.getItems().addAll("plane", "surface");
        cbBgMult.getItems().addAll("1", "10");
    }    
    
    public void setImageSet(ImageSet imgSet) {
        if (imgSet != null) {
            if (imgSet.equals(this.imgSet)) {
                resetValues();
            } else {
                this.imgSet = imgSet;
                tfImageSet.setText(imgSet.toString());
                setDefaultValues();
            }
        } else {
            tfImageSet.setText("");
        }
    }
    
    private void resetValues() {
        /* reset widgets when the dialog window is shown again (same image set) */        
        setBadRegionGroup();
    }

    private void setDefaultValues() {
        /* initialize widgets with default values upon change of image set */
        cbBgModel.setValue("plane");
        cbBgMult.setValue("10");
        setBadRegionGroup();
    }
    
    private void setBadRegionGroup() {
        // set default radiobuttons depending on existance of bad region file
        System.out.println("running setBadRegionGroup()");
        // check for existing bad regions file
        boolean badFileExists = false;
        String badRegName = imgSet.getSetname() + ".badbg.reg";
        File bgcorrDir = new File(imgSet.getProjectDir() + "/bgcorr");
        if (bgcorrDir.exists()) {
            System.out.println("checking for " + imgSet.getProjectDir() + "/bgcorr/" + badRegName);
            File badReg = new File(imgSet.getProjectDir() + "/bgcorr/" + badRegName);
            badFileExists = badReg.exists();
        }
        rbBadFile.setSelected(badFileExists);
        rbBadFile.setDisable(! badFileExists);
        rbBadFrame.setSelected(! badFileExists);
    }
    
    public boolean getOverwrite() {
        return rbBadFrame.isSelected();
    }
    
    public String[] getValues() {
        String[] sarray;
        sarray = new String[] {
                cbBgModel.getValue()
                ,cbBgMult.getValue()
        };
        return sarray;
    }
}
