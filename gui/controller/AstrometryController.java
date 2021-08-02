/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package tl.airtoolsgui.controller;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;
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
import java.util.logging.Level;
import java.util.logging.Logger;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import javafx.beans.property.SimpleStringProperty;
import javafx.beans.property.StringProperty;
import javafx.collections.FXCollections;
import javafx.event.ActionEvent;
import javafx.fxml.FXML;
import javafx.fxml.Initializable;
import javafx.scene.Node;
import javafx.scene.control.Button;
import javafx.scene.control.CheckBox;
import javafx.scene.control.ChoiceBox;
import javafx.scene.control.DatePicker;
import javafx.scene.control.Label;
import javafx.scene.control.RadioButton;
import javafx.scene.control.TextField;
import javafx.scene.control.ToggleGroup;
import javafx.scene.layout.AnchorPane;
import javafx.scene.layout.HBox;
import javafx.scene.layout.VBox;
import javafx.stage.DirectoryChooser;
import javafx.stage.Stage;
import tl.airtoolsgui.model.AirtoolsCLICommand;
import tl.airtoolsgui.model.ImageSet;
import tl.airtoolsgui.model.ShellScript;
import tl.airtoolsgui.model.SimpleLogger;

/**
 * FXML Controller class
 *
 * @author lehmann
 */
public class AstrometryController implements Initializable {

    @FXML
    private AnchorPane paneAstrometry;
    @FXML
    private RadioButton rbCurrProject;
    @FXML
    private ToggleGroup objectsGroup;
    @FXML
    private ChoiceBox<ImageSet> choiceBoxImageSet;
    @FXML
    private RadioButton rbMultProject;
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
    private CheckBox cbShowCheckImages;
    @FXML
    private CheckBox cbCombineResults;
    @FXML
    private Label labelWarning;
    @FXML
    private Button buttonStart;
    @FXML
    private Button buttonCancel;
    @FXML
    private HBox hboxCurrProject;
    @FXML
    private VBox vboxMultProject;

    private SimpleLogger logger;
    private StringProperty projectDir = new SimpleStringProperty();
    private AirtoolsCLICommand aircliCmd;
    private final String aircliTask = "usercmd";
    private final String airfunFunc = "AIastrometry";
    private final List<ImageSet> imageSetList = new ArrayList<>();

    /**
     * Initializes the controller class.
     */
    @Override
    public void initialize(URL url, ResourceBundle rb) {
        paneAstrometry.setOnMouseClicked(event -> {
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
        
        // show/hide widgets depending on choice of radiobutton
        rbMultProject.selectedProperty().addListener((v, oldValue, newValue) -> {
            hboxCurrProject.setDisable(newValue);
            vboxMultProject.setDisable(! newValue);
        });
        rbMultProject.setSelected(false);
        vboxMultProject.setDisable(true);
        
    }    

    public void setReferences (ShellScript sh, SimpleLogger logger, StringProperty projectDir) {
        this.logger = logger;
        this.projectDir = projectDir;
        this.aircliCmd = new AirtoolsCLICommand(buttonStart, logger, sh);
        
        populateChoiceBoxImageSet();
        tfBaseDir1.setText(new File(projectDir.getValue()).getParent());

        labelWarning.setText("");
    }
    

    public void updateWidgets () {
        populateChoiceBoxImageSet();
    }
    
    
    private void populateChoiceBoxImageSet() {
        System.out.println("populateChoiceBoxImageSet()");
        setImageSetList();
        ImageSet allImages = new ImageSet(projectDir.getValue(), "all", "any object", 1);
        imageSetList.add(0, allImages);
        choiceBoxImageSet.setItems(FXCollections.observableArrayList(
            imageSetList));
        choiceBoxImageSet.getSelectionModel().selectFirst();
    }

    
    private void setImageSetList () {
        System.out.println("setImageSetList");
        BufferedReader inFile = null;
        try {
            inFile = new BufferedReader(new FileReader(projectDir.getValue() + "/set.dat"));
            String line;
            // lights only: grep -E "^[0-9]{2}:[0-9]{2}[ ]+[a-zA-Z0-9]+[ ]+[a-zA-Z0-9-]+[ ]+[o][ ]+" set.dat
            Pattern regexp = Pattern.compile("^[0-9]{2}:[0-9]{2}[ ]+[a-zA-Z0-9]+[ ]+[a-zA-Z0-9-]+[ ]+[o][ ]+");
            Matcher matcher = regexp.matcher("");
            imageSetList.clear();
            try {
                while (( line = inFile.readLine()) != null){
                    matcher.reset(line);
                    if (matcher.find()) {
                        String[] columns = line.split("[ ]+");
                        if (columns.length >= 11) {
                            // Note: does require telid in field 11
                            System.out.println(line);
                            imageSetList.add(new ImageSet(projectDir.getValue(), columns[1], columns[2], 1));
                        }
                    }
                }
            } catch (IOException ex) {
                Logger.getLogger(CometPhotometryController.class.getName()).log(Level.SEVERE, null, ex);
            }
        } catch (FileNotFoundException ex) {
            Logger.getLogger(CometPhotometryController.class.getName()).log(Level.SEVERE, null, ex);
        } finally {
            try {
                inFile.close();
            } catch (IOException ex) {
                Logger.getLogger(CometPhotometryController.class.getName()).log(Level.SEVERE, null, ex);
            }
        }
    }
    
    
    private boolean isValidInputs() {
        String msg="";
        LocalDate ld;
        
        if (rbMultProject.isSelected() && tfCometName.getText().isBlank()) {
            msg="ERROR: comet name is missing.";
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
        Stage stage = (Stage) paneAstrometry.getScene().getWindow();
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
        Stage stage = (Stage) paneAstrometry.getScene().getWindow();
        file = dirChooser.showDialog(stage);
        if (file != null) {
            // TODO: check if dir exists and is empty, else show a warning message
            tfBaseDir2.setText(file.getAbsolutePath());
        }
    }

    @FXML
    private void onButtonStart(ActionEvent event) {
        System.out.println("AstrometryController: onButtonStart()");
        labelWarning.setText("");
        List<String> aircliCmdOpts = new ArrayList<>();
        List<String> aircliCmdArgs = new ArrayList<>();
        DateTimeFormatter fmt = DateTimeFormatter.ofPattern("yyyyMMdd");

        if (! isValidInputs()) return;

        // airfun function to call
        aircliCmdArgs.add(airfunFunc);
        
        // add options
        if (cbShowCheckImages.isSelected()) aircliCmdArgs.add("-i");
        if (cbCombineResults.isSelected())  aircliCmdArgs.add("-a");
        
        // add positional parameters
        if (rbMultProject.isSelected()) {
            if (! tfBaseDir1.getText().isBlank()) {
                aircliCmdArgs.add("-d " + tfBaseDir1.getText());
            }
            if (! tfBaseDir2.getText().isBlank()) {
                aircliCmdArgs.add("-d " + tfBaseDir2.getText());
            }
        
            aircliCmdArgs.add(tfCometName.getText());
            if (dpStart.getValue() != null) {
                aircliCmdArgs.add(dpStart.getValue().format(fmt));
            } else {
                aircliCmdArgs.add("\"\"");
            }
            if (dpEnd.getValue() != null) {
                aircliCmdArgs.add(dpEnd.getValue().format(fmt));
            }
        } else {
            aircliCmdArgs.add(choiceBoxImageSet.getSelectionModel().getSelectedItem().getSetname());
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
