/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package tl.airtoolsgui.controller;

import java.net.URL;
import java.util.ResourceBundle;
import javafx.fxml.FXML;
import javafx.fxml.Initializable;
import javafx.scene.control.CheckBox;
import javafx.scene.control.ComboBox;
import javafx.scene.control.DialogPane;
import javafx.scene.control.Label;
import javafx.scene.control.TextField;
import tl.airtoolsgui.model.ImageSet;

/**
 * FXML Controller class
 *
 * @author lehmann
 */
public class PSFExtractController implements Initializable {

    @FXML
    private DialogPane paramDialogPane;
    @FXML
    private TextField tfImageSet;
    @FXML
    private TextField tfRLim;
    @FXML
    private TextField tfMerrLim;
    @FXML
    private ComboBox<String> cbPsfSize;
    @FXML
    private CheckBox cbDelete;
    @FXML
    private Label labelWarning;
    @FXML
    private Label labelDelete;

    private ImageSet imgSet;

    /**
     * Initializes the controller class.
     */
    @Override
    public void initialize(URL url, ResourceBundle rb) {
        // disable unimplemented checkbox
        //labelDelete.setDisable(true);
        //cbDelete.setDisable(true);
        
        labelWarning.setText("");
        cbPsfSize.getItems().addAll("", "80", "128", "184", "256");        

        tfRLim.setText("8");
        setDefaultValues();
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
        cbDelete.setSelected(false);
    }

    private void setDefaultValues() {
        /* initialize widgets with default values upon change of image set */
        /* tfRLim is kept for all image sets */
        tfMerrLim.setText("0.2");
        cbPsfSize.setValue("");
        cbDelete.setSelected(false);
    }
    
    public boolean getOverwrite() {
        return cbDelete.isSelected();
    }

    public String[] getValues() {
        String[] sarray;
        sarray = new String[] {tfRLim.getText()
                ,tfMerrLim.getText()
                ,cbPsfSize.getValue()
        };
        return sarray;
    }
}
