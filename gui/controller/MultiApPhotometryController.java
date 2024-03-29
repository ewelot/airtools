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
import javafx.stage.DirectoryChooser;
import javafx.stage.Stage;
import tl.airtoolsgui.model.AirtoolsCLICommand;
import tl.airtoolsgui.model.ShellScript;
import tl.airtoolsgui.model.SimpleLogger;

/**
 * FXML Controller class
 *
 * @author lehmann
 */
public class MultiApPhotometryController implements Initializable {

    @FXML
    private AnchorPane paneMultiApPhotometry;
    @FXML
    private TextField tfCometName;
    @FXML
    private TextField tfBaseDir1;
    @FXML
    private Button buttonBrowseBaseDir1;
    @FXML
    private TextField tfBaseDir2;
    @FXML
    private Button buttonBrowseBaseDir2;
    @FXML
    private DatePicker dpStart;
    @FXML
    private DatePicker dpEnd;
    @FXML
    private TextField tfApertures;
    @FXML
    private ChoiceBox<ApertureUnit> cbApertureUnit;
    @FXML
    private CheckBox cbShowCheckImages;
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
    private final String airfunFunc = "AImapphot";

    
    private enum ApertureUnit {
        TKM("10^3 kilometer"),
        AMIN("arc seconds");

        private final String label;

        ApertureUnit(String label) {
            this.label = label;
        }

        @Override
        public String toString() {
            return label;
        }
    }

    /**
     * Initializes the controller class.
     */
    @Override
    public void initialize(URL url, ResourceBundle rb) {
        // fill combo boxes
        cbApertureUnit.getItems().setAll(ApertureUnit.values());
        cbApertureUnit.getSelectionModel().selectFirst();
        
        paneMultiApPhotometry.setOnMouseClicked(event -> {
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
        labelWarning.setText("");
    }
    
    private boolean isValidInputs() {
        String msg="";
        LocalDate ld;
        
        if (tfCometName.getText().isBlank()) {
            msg="ERROR: comet name is missing.";
            labelWarning.setText(msg);
            logger.log(msg);
            return false;
        }
        if (tfApertures.getText().isBlank()) {
            msg="ERROR: list of apertures is missing.";
            labelWarning.setText(msg);
            logger.log(msg);
            return false;
        }
        
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
        Stage stage = (Stage) paneMultiApPhotometry.getScene().getWindow();
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
        Stage stage = (Stage) paneMultiApPhotometry.getScene().getWindow();
        file = dirChooser.showDialog(stage);
        if (file != null) {
            // TODO: check if dir exists and is empty, else show a warning message
            tfBaseDir2.setText(file.getAbsolutePath());
        }
    }

    @FXML
    private void onButtonStart(ActionEvent event) {
        System.out.println("MultiApPhotometryController: onButtonStart()");
        labelWarning.setText("");
        List<String> aircliCmdOpts = new ArrayList<>();
        List<String> aircliCmdArgs = new ArrayList<>();

        DateTimeFormatter fmt = DateTimeFormatter.ofPattern("yyyyMMdd");
        ApertureUnit apertureUnit=cbApertureUnit.getSelectionModel().getSelectedItem();
        
        if (! isValidInputs()) return;
        
        // add aircliCmd options
        
        // add airfunFunc options
        // airfun function to call
        aircliCmdArgs.add(airfunFunc);
        
        
        /* always create check images; TODO: allow user to set size */
        aircliCmdArgs.add("-s 300");
        if (apertureUnit == ApertureUnit.TKM) aircliCmdArgs.add("-k");
        if (cbShowCheckImages.isSelected()) aircliCmdArgs.add("-i");
        
        if (! tfBaseDir1.getText().isBlank()) aircliCmdArgs.add("-d " + tfBaseDir1.getText());
        if (! tfBaseDir2.getText().isBlank()) aircliCmdArgs.add("-dd " + tfBaseDir2.getText());
        
        // add parameters
        aircliCmdArgs.add(tfCometName.getText());
        aircliCmdArgs.add("\"" + tfApertures.getText() + "\"");
        
        if (dpStart.getValue() != null) {
            aircliCmdArgs.add(dpStart.getValue().format(fmt));
        }
        if (dpEnd.getValue() != null) {
            if (dpStart.getValue() == null) aircliCmdArgs.add("\"\"");
            aircliCmdArgs.add(dpEnd.getValue().format(fmt));
        }
        
        // run command
        System.out.println("cmd: " + aircliCmdOpts + " " + aircliTask + " " + aircliCmdArgs);
        //logger.log("# cmd: " + aircliCmdOpts + " " + aircliTask + " " + aircliCmdArgs);
        aircliCmd.setOpts(aircliCmdOpts.toArray(new String[0]));
        aircliCmd.setArgs(aircliCmdArgs.toArray(new String[0]));
        aircliCmd.run();
        // paneMultiApPhotometry.getScene().getWindow().hide();
    }

    @FXML
    private void onButtonCancel(ActionEvent event) {
        Node  source = (Node)  event.getSource(); 
        Stage stage  = (Stage) source.getScene().getWindow();
        stage.close();
    }
    
}
