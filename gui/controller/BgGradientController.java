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
public class BgGradientController implements Initializable {

    @FXML
    private DialogPane paramDialogPane;
    @FXML
    private Label labelWarning;
    @FXML
    private TextField tfImageSet;
    @FXML
    private TextField tfBgSample;
    @FXML
    private ComboBox<String> cbBgModel;
    @FXML
    private ComboBox<String> cbBgMult;

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
            tfImageSet.setText(imgSet.toString());
        } else {
            tfImageSet.setText("");
        }
    }
    
    public String[] getValues() {
        String[] sarray;
        sarray = new String[] {tfBgSample.getText()
                ,cbBgModel.getValue()
                ,cbBgMult.getValue()
        };
        return sarray;
    }
    
    public void setValues(String[] sarray) {
        int size=sarray.length;
        if (size > 0) tfBgSample.setText(sarray[0]);
        if (size > 1) cbBgModel.setValue(sarray[1]);
        if (size > 2) cbBgMult.setValue(sarray[2]);
    }
}
