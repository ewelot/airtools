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
public class ManualDataController implements Initializable {

    @FXML
    private DialogPane paramDialogPane;
    @FXML
    private Label labelWarning;
    @FXML
    private TextField tfImageSet;
    @FXML
    private ComboBox<String> cbChannel;
    @FXML
    private TextField tfCCorr;
    @FXML
    private TextField tfStLim;
    @FXML
    private TextField tfDtLen;
    @FXML
    private TextField tfDtAng;
    @FXML
    private TextField tfPtLen;
    @FXML
    private TextField tfPtAng;

    /**
     * Initializes the controller class.
     */
    @Override
    public void initialize(URL url, ResourceBundle rb) {
        labelWarning.setText("");
        cbChannel.getItems().addAll("1", "2", "3");
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
                ,tfCCorr.getText()
                ,tfStLim.getText()
                ,tfDtLen.getText()
                ,tfDtAng.getText()
                ,tfPtLen.getText()
                ,tfPtAng.getText()
        };
        return sarray;
    }
    
    public void setValues(String[] sarray) {
        int size=sarray.length;
        if (size > 0) cbChannel.setValue(sarray[0]);
        if (size > 1) tfCCorr.setText(sarray[1]);
        if (size > 2) tfStLim.setText(sarray[2]);
        if (size > 3) tfDtLen.setText(sarray[3]);
        if (size > 4) tfDtAng.setText(sarray[4]);
        if (size > 5) tfPtLen.setText(sarray[5]);
        if (size > 6) tfPtAng.setText(sarray[6]);
    }
}
