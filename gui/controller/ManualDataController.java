/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package tl.airtoolsgui.controller;

import java.io.FileNotFoundException;
import java.io.IOException;
import java.net.URL;
import java.util.ResourceBundle;
import java.util.logging.Level;
import java.util.logging.Logger;
import javafx.event.ActionEvent;
import javafx.event.EventType;
import javafx.fxml.FXML;
import javafx.fxml.Initializable;
import javafx.scene.control.Button;
import javafx.scene.control.ButtonType;
import javafx.scene.control.ComboBox;
import javafx.scene.control.DialogPane;
import javafx.scene.control.Label;
import javafx.scene.control.TextField;
import tl.airtoolsgui.model.Header;
import tl.airtoolsgui.model.ImageSet;
import tl.airtoolsgui.model.ManualData;

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

    private ImageSet imgSet;

    /**
     * Initializes the controller class.
     */
    @Override
    public void initialize(URL url, ResourceBundle rb) {
        labelWarning.setText("");
        cbChannel.getItems().addAll("1", "2", "3");
        /* TODO: changing channel must trigger updateFromHeader */
        
        // add event filter to validate inputs
        ((Button) paramDialogPane.lookupButton(ButtonType.APPLY)).addEventFilter(
                ActionEvent.ACTION, event -> {
                    if(! isValidInputs()) event.consume();
                }
        );
    }    
    
    public void setImageSet(ImageSet imgSet) {
        if (imgSet != null) {
            if (imgSet.equals(this.imgSet)) {
                resetValues();
            } else {
                this.imgSet = imgSet;
                tfImageSet.setText(imgSet.toString());
                if (imgSet.getStarStack().endsWith(".ppm")) {
                    cbChannel.getItems().setAll("1", "2", "3");
                } else {
                    cbChannel.getItems().setAll("1");
                }
                setDefaultValues();
            }
        } else {
            tfImageSet.setText("");
        }
    }
    
    private void resetValues() {
        /* reset widgets when the dialog window is shown again (same image set) */        
        updateFromHeader(Integer.parseInt(cbChannel.getValue()));
    }

    private void setDefaultValues() {
        String channel = "1";
        if (imgSet.getStarStack().endsWith(".ppm")) channel="2";

        cbChannel.setValue(channel);
        updateFromHeader(Integer.parseInt(channel));
    }
    
    private void updateFromHeader (int plane) {
        // update some widgets with values read from header file according to channel
        // default values
        tfCCorr.setText("");
        tfStLim.setText("");
        tfDtLen.setText("");
        tfDtAng.setText("");
        tfPtLen.setText("");
        tfPtAng.setText("");
        
        try {
            if (imgSet != null) {
                Header head = new Header (imgSet.getProjectDir() + "/" + imgSet.getHeader());

                // find a given entry
                ManualData myManualData = null;
                myManualData = head.getManualData(plane);
                if (myManualData != null) {
                    if (myManualData.getAcor() != -1) {
                        tfCCorr.setText(Integer.toString(myManualData.getAcor()));
                    }
                    if (myManualData.getAlim() != -1) {
                        tfStLim.setText(Integer.toString(myManualData.getAlim()));
                    }
                    if (myManualData.getDlen()!= -1) {
                        tfDtLen.setText(Integer.toString(myManualData.getDlen()));
                    }
                    if (myManualData.getDang()!= -1) {
                        tfDtAng.setText(Integer.toString(myManualData.getDang()));
                    }
                    if (myManualData.getPlen()!= -1) {
                        tfPtLen.setText(Integer.toString(myManualData.getPlen()));
                    }
                    if (myManualData.getPang()!= -1) {
                        tfPtAng.setText(Integer.toString(myManualData.getPang()));
                    }
                }
            }
        } catch (FileNotFoundException exFile) {
            System.out.println("WARNING: header file for " + imgSet.getSetname() + " not found");
            Logger.getLogger(PhotCalibrationController.class.getName()).log(Level.SEVERE, null, exFile);
        } catch (IOException exIO) {
            System.out.println("WARNING: unable to read header file " + imgSet.getHeader());
            Logger.getLogger(PhotCalibrationController.class.getName()).log(Level.SEVERE, null, exIO);
        }
    }
    
    
    private boolean isValidInputs() {
        // NOT yet in use !!
        String msg="";
        String str="";
        int i;
        // check if entries are valid integer numbers
        try {
            str=tfCCorr.getText();
            if (! str.isBlank()) i=Integer.parseInt(str);
            str=tfStLim.getText();
            if (! str.isBlank()) i=Integer.parseInt(str);
            str=tfDtLen.getText();
            if (! str.isBlank()) i=Integer.parseInt(str);
            str=tfDtAng.getText();
            if (! str.isBlank()) i=Integer.parseInt(str);
            str=tfPtLen.getText();
            if (! str.isBlank()) i=Integer.parseInt(str);
            str=tfPtAng.getText();
            if (! str.isBlank()) i=Integer.parseInt(str);
            labelWarning.setText("");
        } catch (NumberFormatException ex) {
            msg="ERROR: value " + str + " is not a number.";
            labelWarning.setText(msg);
            //logger.log(msg);
            return false;            
        }
        return true;
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
}
