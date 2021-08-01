/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package tl.airtoolsgui.controller;

import java.io.File;
import java.net.URL;
import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.time.format.DateTimeParseException;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;
import java.util.ResourceBundle;
import javafx.beans.property.SimpleStringProperty;
import javafx.beans.property.StringProperty;
import javafx.event.ActionEvent;
import javafx.fxml.FXML;
import javafx.fxml.Initializable;
import javafx.scene.Node;
import javafx.scene.control.Button;
import javafx.scene.control.CheckBox;
import javafx.scene.control.ChoiceBox;
import javafx.scene.control.DatePicker;
import javafx.scene.control.Label;
import javafx.scene.control.TextField;
import javafx.scene.layout.AnchorPane;
import javafx.scene.layout.VBox;
import javafx.stage.DirectoryChooser;
import javafx.stage.Stage;
import tl.airtoolsgui.model.AirtoolsCLICommand;
import tl.airtoolsgui.model.PhotCatalog;
import tl.airtoolsgui.model.ShellScript;
import tl.airtoolsgui.model.SimpleLogger;

/**
 * FXML Controller class
 *
 * @author lehmann
 */
public class ListResultsController implements Initializable {

    @FXML
    private AnchorPane paneListResults;
    @FXML
    private TextField tfBaseDir1;
    @FXML
    private Button buttonBrowseBaseDir1;
    @FXML
    private TextField tfBaseDir2;
    @FXML
    private Button buttonBrowseBaseDir2;
    @FXML
    private TextField tfCometName;
    @FXML
    private DatePicker dpStart;
    @FXML
    private DatePicker dpEnd;
    @FXML
    private ChoiceBox<PhotCatalog> choiceBoxPhotCat;
    @FXML
    private CheckBox cbShowUncalibrated;
    @FXML
    private CheckBox cbTexp;
    @FXML
    private CheckBox cbNexp;
    @FXML
    private CheckBox cbPscale;
    @FXML
    private CheckBox cbRot;
    @FXML
    private CheckBox cbBg;
    @FXML
    private CheckBox cbRms;
    @FXML
    private CheckBox cbFwhm;
    @FXML
    private CheckBox cbNfit;
    @FXML
    private CheckBox cbMrms;
    @FXML
    private CheckBox cbCcoeff;
    @FXML
    private TextField tfAddOptions;
    @FXML
    private Label labelWarning;
    @FXML
    private Button buttonStart;
    @FXML
    private Button buttonCancel;

    private SimpleLogger logger;
    private StringProperty projectDir = new SimpleStringProperty();
    private AirtoolsCLICommand aircliCmd;
    private final String aircliTask = "usercmd";
    private final String airfunFunc = "AIlist";

    /**
     * Initializes the controller class.
     */
    @Override
    public void initialize(URL url, ResourceBundle rb) {
        // fill choice boxes
        // TODO: read from refcat.dat
        choiceBoxPhotCat.getItems().addAll(
                new PhotCatalog("preferred", "preferred catalog", new String[]{}, ""),
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
                        "V+c(B-V)"),
                new PhotCatalog("all", "any catalog", new String[]{}, "")
        );
        
        paneListResults.setOnMouseClicked(event -> {
            labelWarning.setText("");
        });

        // obtaining prompt text for date inputs does not work as expected
        String pattern = ((SimpleDateFormat) DateFormat.getDateInstance(DateFormat.SHORT, Locale.getDefault())).toPattern();
        System.out.println("default pattern: " + pattern + " (current locale: " + Locale.getDefault() + ")");
        
        // set prompt text for date picker
        String lang = Locale.getDefault().getLanguage();
        switch (lang) {
            case "en":
                pattern="mm/dd/yyyy";
                break;
            case "de":
                pattern="dd.mm.yyyy";
                break;
            default:
                pattern="";
                break;
        }
        dpStart.setPromptText(pattern);
        dpEnd.setPromptText(pattern);
    }    

    public void setReferences (ShellScript sh, SimpleLogger logger, StringProperty projectDir) {
        this.logger = logger;
        this.projectDir = projectDir;
        this.aircliCmd = new AirtoolsCLICommand(buttonStart, logger, sh);

        tfBaseDir1.setText(new File(projectDir.getValue()).getParent());
        choiceBoxPhotCat.getSelectionModel().selectFirst();
        labelWarning.setText("");
    }
    

    private boolean isValidInputs() {
        String msg="";
        LocalDate ld;
        /*
        if (tfCometName.getText().isBlank()) {
            msg="ERROR: comet name is missing.";
            labelWarning.setText(msg);
            logger.log(msg);
            return false;
        }
        */
        
        // format datepicker text entries
        if (! dpStart.getEditor().getText().isBlank()) {
            try {
                ld=dpStart.getConverter().fromString(dpStart.getEditor().getText());
                dpStart.setValue(ld);
            } catch (DateTimeParseException ex) {
                msg="ERROR: entered string of start date does not match date format.";
                labelWarning.setText(msg);
                logger.log(msg);
                return false;
            }
        } else dpStart.setValue(null);
        if (! dpEnd.getEditor().getText().isBlank()) {
            try {
                ld=dpEnd.getConverter().fromString(dpEnd.getEditor().getText());
                dpEnd.setValue(ld);
            } catch (DateTimeParseException ex) {
                msg="ERROR: entered string of end date does not match date format.";
                labelWarning.setText(msg);
                logger.log(msg);
                return false;
            }
        } else dpEnd.setValue(null);
        if (dpStart.getValue() != null && dpEnd.getValue() != null &&
                dpStart.getValue().isAfter(dpEnd.getValue())) {
            msg="ERROR: start date is after end date.";
            labelWarning.setText(msg);
            logger.log(msg);
            return false;
        }
        return true;
    }
    
    
    @FXML
    private void onButtonBrowseBaseDir1(ActionEvent event) {
        DirectoryChooser dirChooser = new DirectoryChooser();
        String dirName = tfBaseDir1.getText();
        File f;
        
        if (dirName.isEmpty()) {
            f = new File(projectDir.getValue());
            dirName=f.getParent();
        }

        File file = new File(dirName);
        if (! file.isDirectory()) {
            dirName = file.getParent();
            file = new File(dirName);
            if (! file.isDirectory()) {
                dirName = file.getParent();
                file = new File(dirName);
                if (! file.isDirectory()) {
                    f = new File(projectDir.getValue());
                    dirName=f.getParent();
                    file = new File(dirName);
                }
            }
        }
        dirChooser.setInitialDirectory(file);
        Stage stage = (Stage) paneListResults.getScene().getWindow();
        file = dirChooser.showDialog(stage);
        if (file != null) {
            // TODO: check if dir exists and is empty, else show a warning message
            tfBaseDir1.setText(file.getAbsolutePath());
        }
    }

    @FXML
    private void onButtonBrowseBaseDir2(ActionEvent event) {
        DirectoryChooser dirChooser = new DirectoryChooser();
        String dirName = tfBaseDir2.getText();
        File f;
        
        if (dirName.isEmpty()) {
            f = new File(projectDir.getValue());
            dirName=f.getParent();
        }

        File file = new File(dirName);
        if (! file.isDirectory()) {
            dirName = file.getParent();
            file = new File(dirName);
            if (! file.isDirectory()) {
                dirName = file.getParent();
                file = new File(dirName);
                if (! file.isDirectory()) {
                    f = new File(projectDir.getValue());
                    dirName=f.getParent();
                    file = new File(dirName);
                }
            }
        }
        dirChooser.setInitialDirectory(file);
        Stage stage = (Stage) paneListResults.getScene().getWindow();
        file = dirChooser.showDialog(stage);
        if (file != null) {
            // TODO: check if dir exists and is empty, else show a warning message
            tfBaseDir2.setText(file.getAbsolutePath());
        }
    }

    @FXML
    private void onButtonStart(ActionEvent event) {
        System.out.println("ListResultsController: onButtonStart()");
        labelWarning.setText("");
        List<String> aircliCmdOpts = new ArrayList<>();
        List<String> aircliCmdArgs = new ArrayList<>();
        StringBuilder addFields = new StringBuilder();

        DateTimeFormatter fmt = DateTimeFormatter.ofPattern("yyyyMMdd");
        String photCat=choiceBoxPhotCat.getSelectionModel().getSelectedItem().getId();
        
        if (! isValidInputs()) return;
        
        // airfun function to call
        aircliCmdArgs.add(airfunFunc);
                
        // add options
        aircliCmdArgs.add("-w");    // show results in text editor window
        if (! photCat.equalsIgnoreCase("preferred")) aircliCmdArgs.add("-p " + photCat);
        if (cbShowUncalibrated.isSelected()) aircliCmdArgs.add("-a");
        
        if (! tfBaseDir1.getText().isBlank()) aircliCmdArgs.add("-d " + tfBaseDir1.getText());
        if (! tfBaseDir2.getText().isBlank()) aircliCmdArgs.add("-d " + tfBaseDir2.getText());
        if (tfBaseDir1.getText().isBlank() && tfBaseDir2.getText().isBlank())
            aircliCmdArgs.add("-c");

        // additional fields
        if (cbTexp.isSelected()) {
            if (addFields.length() > 0) addFields.append(",");
            addFields.append("texp");
        }
        if (cbNexp.isSelected()) {
            if (addFields.length() > 0) addFields.append(",");
            addFields.append("nexp");
        }
        if (cbPscale.isSelected()) {
            if (addFields.length() > 0) addFields.append(",");
            addFields.append("pscale");
        }
        if (cbRot.isSelected()) {
            if (addFields.length() > 0) addFields.append(",");
            addFields.append("rot");
        }
        if (cbBg.isSelected()) {
            if (addFields.length() > 0) addFields.append(",");
            addFields.append("bg");
        }
        if (cbRms.isSelected()) {
            if (addFields.length() > 0) addFields.append(",");
            addFields.append("rms");
        }
        if (cbFwhm.isSelected()) {
            if (addFields.length() > 0) addFields.append(",");
            addFields.append("fwhm");
        }
        if (cbNfit.isSelected()) {
            if (addFields.length() > 0) addFields.append(",");
            addFields.append("nfit");
        }
        if (cbMrms.isSelected()) {
            if (addFields.length() > 0) addFields.append(",");
            addFields.append("mrms");
        }
        if (cbCcoeff.isSelected()) {
            if (addFields.length() > 0) addFields.append(",");
            addFields.append("ccoeff");
        }
        if (addFields.length() > 0) aircliCmdArgs.add("-f " + addFields);

        if (! tfAddOptions.getText().isBlank()) {
            aircliCmdArgs.add(tfAddOptions.getText());
        }

        
        // add parameters
        if (! tfCometName.getText().isBlank()) {
            aircliCmdArgs.add(tfCometName.getText());
        } else {
            if (dpStart.getValue() != null || dpEnd.getValue() != null)
                aircliCmdArgs.add("\"\"");
        }
        if (dpStart.getValue() != null) {
            aircliCmdArgs.add(dpStart.getValue().format(fmt));
        } else {
            if (dpEnd.getValue() != null)
                aircliCmdArgs.add("\"\"");
        }
        if (dpEnd.getValue() != null) {
            aircliCmdArgs.add(dpEnd.getValue().format(fmt));
        }
        
        // run command
        System.out.println("cmd: " + aircliCmdOpts + " " + aircliTask + " " + aircliCmdArgs);
        //logger.log("# cmd: " + aircliCmdOpts + " " + aircliTask + " " + aircliCmdArgs);
        aircliCmd.setOpts(aircliCmdOpts.toArray(new String[0]));
        aircliCmd.setArgs(aircliCmdArgs.toArray(new String[0]));
        aircliCmd.run();
    }

    @FXML
    private void onButtonCancel(ActionEvent event) {
        Node  source = (Node)  event.getSource(); 
        Stage stage  = (Stage) source.getScene().getWindow();
        stage.close();
    }
    
}
