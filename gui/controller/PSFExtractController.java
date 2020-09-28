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
    private Label labelWarning;

    /**
     * Initializes the controller class.
     */
    @Override
    public void initialize(URL url, ResourceBundle rb) {
        labelWarning.setText("");
        cbPsfSize.getItems().addAll("80", "128", "184", "256");        
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
        sarray = new String[] {tfRLim.getText()
                ,tfMerrLim.getText()
                ,cbPsfSize.getValue()
        };
        return sarray;
    }
    
    public void setValues(String[] sarray) {
        int size=sarray.length;
        if (size > 0) tfRLim.setText(sarray[0]);
        if (size > 1) tfMerrLim.setText(sarray[1]);
        if (size > 2) cbPsfSize.setValue(sarray[2]);
    }
    
}
