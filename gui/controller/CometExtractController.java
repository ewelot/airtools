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
public class CometExtractController implements Initializable {

    @FXML
    private DialogPane paramDialogPane;
    @FXML
    private Label labelWarning;
    @FXML
    private TextField tfImageSet;
    @FXML
    private TextField tfBgImage;
    @FXML
    private ComboBox<String> cbCoMult;
    @FXML
    private ComboBox<String> cbMaxRadius;

    /**
     * Initializes the controller class.
     */
    @Override
    public void initialize(URL url, ResourceBundle rb) {
        labelWarning.setText("");
        cbCoMult.getItems().addAll("1", "10");
        cbMaxRadius.getItems().addAll("10", "100");
    }    
    
    public void setImageSet(ImageSet imgSet) {
        if (imgSet != null) {
            tfImageSet.setText(imgSet.toString());
        } else {
            tfImageSet.setText("");
        }
    }
    
    public String[] getValues() {
        String[] sarray;
        sarray = new String[] {tfBgImage.getText()
                ,cbCoMult.getValue()
                ,cbMaxRadius.getValue()
        };
        return sarray;
    }
    
    public void setValues(String[] sarray) {
        int size=sarray.length;
        if (size > 0) tfBgImage.setText(sarray[0]);
        if (size > 1) cbCoMult.setValue(sarray[1]);
        if (size > 2) cbMaxRadius.setValue(sarray[2]);
    }
}
