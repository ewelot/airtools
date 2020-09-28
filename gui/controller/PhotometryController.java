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
public class PhotometryController implements Initializable {

    @FXML
    private DialogPane paramDialogPane;
    @FXML
    private Label labelWarning;
    @FXML
    private TextField tfImageSet;
    @FXML
    private ComboBox<String> cbChannel;
    @FXML
    private ComboBox<String> cbCatalog;
    @FXML
    private ComboBox<String> cbColor;
    @FXML
    private TextField tfApRad;
    @FXML
    private TextField tfTOpts;
    @FXML
    private TextField tfAOpts;
    @FXML
    private TextField tfSkip;
    /*
    @FXML
    private CheckBox cbDoExOut;
    */
    
    /**
     * Initializes the controller class.
     */
    @Override
    public void initialize(URL url, ResourceBundle rb) {
        labelWarning.setText("");
        cbChannel.getItems().addAll("1", "2", "3");
        cbCatalog.getItems().addAll("APASS", "Tycho2", "Sky2000");
        cbColor.getItems().addAll("B+c(B-V)", "V", "V+c(B-V)", "V+c(V-R)", "R+c(V-R)");
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
        sarray = new String[] {cbChannel.getValue()
                ,cbCatalog.getValue().toLowerCase()
                ,cbColor.getValue()
                ,tfApRad.getText()
                ,tfTOpts.getText()
                ,tfAOpts.getText()
                ,tfSkip.getText()
        };
        return sarray;
    }
    
    public void setValues(String[] sarray) {
        int size=sarray.length;
        if (size > 0) cbChannel.setValue(sarray[0]);
        if (size > 1) cbCatalog.setValue(sarray[1]);
        if (size > 2) cbColor.setValue(sarray[2]);
        if (size > 3) tfApRad.setText(sarray[3]);
        if (size > 4) tfTOpts.setText(sarray[4]);
        if (size > 5) tfAOpts.setText(sarray[5]);
        if (size > 6) tfSkip.setText(sarray[6]);
    }
}
