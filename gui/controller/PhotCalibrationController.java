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
import javafx.fxml.FXML;
import javafx.fxml.Initializable;
import javafx.scene.control.CheckBox;
import javafx.scene.control.ComboBox;
import javafx.scene.control.DialogPane;
import javafx.scene.control.Label;
import javafx.scene.control.TextField;
import tl.airtoolsgui.model.Header;
import tl.airtoolsgui.model.ImageSet;
import tl.airtoolsgui.model.PhotCatalog;
import tl.airtoolsgui.model.PhotEntry;

/**
 * FXML Controller class
 *
 * @author lehmann
 */
public class PhotCalibrationController implements Initializable {

    @FXML
    private DialogPane paramDialogPane;
    @FXML
    private TextField tfImageSet;
    @FXML
    private ComboBox<String> cbChannel;
    @FXML
    private ComboBox<PhotCatalog> cbCatalog;
    @FXML
    private ComboBox<String> cbColor;
    @FXML
    private TextField tfMaxStars;
    @FXML
    private TextField tfApRad;
    @FXML
    private TextField tfMagLim;
    @FXML
    private CheckBox cbExtinction;
    @FXML
    private TextField tfSkip;
    @FXML
    private TextField tfExpert;
    @FXML
    private Label labelDelete;
    @FXML
    private CheckBox cbDelete;
    @FXML
    private Label labelWarning;
    
    private ImageSet imgSet;

    /**
     * Initializes the controller class.
     */
    @Override
    public void initialize(URL url, ResourceBundle rb) {
        labelWarning.setText("");

        // add combobox items
        cbChannel.getItems().addAll("1", "2", "3");
        cbCatalog.getItems().addAll(
                new PhotCatalog("apass",   "APASS DR9",
                        new String[]{ "B", "B+c(B-V)", "V", "V+c(B-V)", "V+c(V-R)", "R", "R+c(V-R)" },
                        "V+c(B-V)"),
                new PhotCatalog("gaia3e",  "Gaia EDR3",
                        new String[]{ "GB", "GB+c(GB-G)", "GB+c(GB-GR)", "G", "G+c(GB-G)", "G+c(GB-GR)"},
                        "GB+c(GB-GR)"),
                new PhotCatalog("tycho2",  "Tycho2",
                        new String[]{ "BT", "BT+c(BT-VT)", "VT", "VT+c(BT-VT)" },
                        "VT+c(BT-VT)"),
                new PhotCatalog("sky2000", "Sky2000",
                        new String[]{ "B", "B+c(B-V)", "V", "V+c(B-V)" },
                        "V+c(B-V)")
        );
        cbColor.getItems().addAll(cbCatalog.getItems().get(0).getColorFit());
        
        // add combobox change listeners
        cbCatalog.setOnAction((event) -> {
            PhotCatalog newPhotCat = cbCatalog.getValue(); //getSelectionModel().getSelectedItem();
            int plane = Integer.valueOf(cbChannel.getValue());
            cbColor.getItems().clear();
            cbColor.getItems().addAll(newPhotCat.getColorFit());
            updateFromHeader(newPhotCat, plane);
            tfSkip.setText("");
            cbDelete.setSelected(false);
        });

        /* TODO: recognize change of channel */

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
        updateFromHeader(cbCatalog.getValue(), Integer.parseInt(cbChannel.getValue()));
        cbDelete.setSelected(false);        
    }

    private void setDefaultValues() {
        // set default values in GUI widgets
        int plane       = 1;
        if (imgSet != null && imgSet.getStarStack().endsWith(".ppm")) plane=2;
        PhotCatalog refcat  = cbCatalog.getItems().get(0);
        String doext    = "";
        String skip     = "";
        String opts     = "";
        String dodel    = "";
        
        // update widgets
        cbChannel.setValue(Integer.toString(plane));
        cbCatalog.setValue(refcat);
        updateFromHeader(refcat, plane);
        cbExtinction.setSelected(!doext.isBlank());
        tfSkip.setText(skip);
        tfExpert.setText(opts);
        cbDelete.setSelected(false);
    }
    
    public boolean getOverwrite() {
        return cbDelete.isSelected();
    }

    public String[] getValues() {
        // get values from GUI widgets
        String[] sarray;
        sarray = new String[] {cbChannel.getValue()
                ,cbCatalog.getSelectionModel().getSelectedItem().getId()
                ,cbColor.getValue()
                ,tfMaxStars.getText()
                ,tfApRad.getText()
                ,tfMagLim.getText()
                ,cbExtinction.isSelected() ? "1" : ""
                ,tfSkip.getText()
                ,tfExpert.getText()
                ,cbDelete.isSelected() ? "1" : ""
        };
        return sarray;
    }
    
    private void updateFromHeader (PhotCatalog refcat, int plane) {
        // update some widgets with values read from header file according to refcat and channel
        // set default values
        String color    = refcat.getDefaultVFit();
        int maxstars    = 200;
        String aprad    = "";
        String maglim   = "";
        
        // read last used parameters from image header file
        try {
            if (imgSet != null) {
                Header head = new Header (imgSet.getProjectDir() + "/" + imgSet.getHeader());

                // find a given entry
                PhotEntry myPhotEntry = null;
                myPhotEntry = head.getPhotEntry(plane, refcat.getId());
                if (myPhotEntry != null) {
                    System.out.println(myPhotEntry.show());
                    if (myPhotEntry.getPcol() != null)
                        color=myPhotEntry.getPcol();
                    if (myPhotEntry.getCind() != null && ! myPhotEntry.getCind().isBlank())
                        color+="+c(" + myPhotEntry.getCind() + ")";
                    if (myPhotEntry.getNmax() > 0)
                        maxstars=myPhotEntry.getNmax();
                    if (myPhotEntry.getArad() > 0)
                        aprad=Double.toString(myPhotEntry.getArad());
                    if (myPhotEntry.getRlim() > 0)
                        maglim=Double.toString(myPhotEntry.getRlim());
                } else {
                    System.out.println("WARNING: photometry entry for plane=" + plane + " catalog=" + refcat.getId() + " not found");
                }
            }
        } catch (FileNotFoundException exFile) {
            System.out.println("WARNING: header file for " + imgSet.getSetname() + " not found");
            Logger.getLogger(PhotCalibrationController.class.getName()).log(Level.SEVERE, null, exFile);
        } catch (IOException exIO) {
            System.out.println("WARNING: unable to read header file " + imgSet.getHeader());
            Logger.getLogger(PhotCalibrationController.class.getName()).log(Level.SEVERE, null, exIO);
        }
        
        // update widgets
        cbColor.setValue(color);
        tfMaxStars.setText(Integer.toString(maxstars));
        tfApRad.setText(aprad);
        tfMagLim.setText(maglim);
    }
}
