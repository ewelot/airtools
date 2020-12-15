/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package tl.airtoolsgui;

import tl.airtoolsgui.controller.MainController;
import tl.airtoolsgui.model.SimpleLogger;
import tl.airtoolsgui.model.ShellScript;
import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.OutputStream;
import java.util.Optional;
import java.util.Properties;
import java.util.logging.Level;
import java.util.logging.Logger;
import javafx.application.Application;
import javafx.application.Platform;
import javafx.beans.binding.Bindings;
import javafx.beans.property.SimpleStringProperty;
import javafx.beans.property.StringProperty;
import javafx.fxml.FXMLLoader;
import javafx.scene.Parent;
import javafx.scene.Scene;
import javafx.scene.control.Button;
import javafx.scene.control.ButtonType;
import javafx.scene.control.Dialog;
import javafx.scene.control.DialogPane;
import javafx.stage.Modality;
import javafx.stage.Stage;
import tl.airtoolsgui.controller.SetupAirtoolsController;

/**
 *
 * @author lehmann
 */
public class AirtoolsGUI extends Application {
    
    private final String progVersion = "3.3.2";
    private final String progDate = "2020-12-11";
    private final String confFileName = "airtools.conf";
    private final String scriptFileName = "airtools-cli";
    
    private static String addPath = "";
    
    @Override
    public void start(Stage stage) throws Exception {
        String absoluteConfFileName = System.getenv("HOME") + "/.airtools/"
            + majorVersion(progVersion) + "/" + confFileName;
        boolean isFirstProject = false;
        if (requiresSetup(absoluteConfFileName)) {
            setupAirtools(absoluteConfFileName);
            isFirstProject = true;
        }
        
        SimpleLogger logger = new SimpleLogger();
        ShellScript sh = new ShellScript();
        if (! addPath.isEmpty()) System.out.println("addPath=" + addPath);
        sh.setFileName(scriptFileName);
        sh.setAddPath(addPath);
        sh.setLog(logger);
        
        FXMLLoader loader = new FXMLLoader(getClass().getResource("/tl/airtoolsgui/view/Main.fxml"));
        Parent root = loader.load();
        
        Scene scene = new Scene(root);
        
        final MainController controller = loader.getController();
        controller.setReferences(absoluteConfFileName, sh, logger, progVersion, progDate);
        
        stage.setScene(scene);
        
        // Setting window title
        StringProperty projectDay = new SimpleStringProperty();        
        projectDay.bind(Bindings.createStringBinding(() -> {
            String pDir = controller.getProjectDir().getValue();
            int start=pDir.lastIndexOf("/") + 1;
            return pDir.substring(start);
        }, controller.getProjectDir()));
        stage.titleProperty().bind(Bindings.concat("AIRTOOLS - ").concat(projectDay));

        stage.setOnHidden(e -> Platform.exit());
        stage.show();
        stage.setMinWidth(stage.getWidth());
        stage.setMinHeight(stage.getHeight());
        stage.setMaxWidth(2000);
        stage.setMaxHeight(1400);

        if (isFirstProject) {
            // open "New Project" dialog
            Platform.runLater(() -> {
                controller.showNewProjectDialog();
            });
        }
    }

    /**
     * @param args the command line arguments
     */
    public static void main(String[] args) {
        int i=0;
        String arg;
        while (i < args.length && args[i].startsWith("-")) {
            arg = args[i++];

            if (arg.equals("-p")) {
                if (i < args.length) {
                    addPath = args[i++];
                } else {
                    System.err.println("-p requires a path argument");
                    System.exit(255);
                }
            }
            
            if (arg.equals("-a")) {
                System.out.println("# using antialias font settings: prism.text=t2k prism.lcdtext=false");
                System.setProperty("prism.text", "t2k");
                System.setProperty("prism.lcdtext", "false");
            }
        }

        launch(args);
    }

    private String majorVersion (String version) {
        int pos = version.indexOf(".");
        return pos >= 0 ? version.substring(0, pos) : version;
    }
    
    private boolean requiresSetup (String confFileName) {
        boolean answer = false;
        File file = new File(confFileName);
        if (file.exists()) {
            if (file.length() == 0) answer=true;
        } else {
            answer = true;
        }
        return answer;
    }
    
    private void setupAirtools(String confFileName) {
        try {
            FXMLLoader loader = new FXMLLoader(getClass().getResource("/tl/airtoolsgui/view/SetupAirtools.fxml"));
            DialogPane pane = (DialogPane) loader.load();
            SetupAirtoolsController controller = loader.getController();

            // create dialog
            Dialog dialog = new Dialog();
            dialog.setDialogPane((DialogPane) pane);
            dialog.setTitle("Setup Airtools");
            dialog.initModality(Modality.WINDOW_MODAL);
            //dialog.initOwner(pane.getScene().getWindow());

            ((Button) pane.lookupButton(ButtonType.APPLY)).setText("Apply");
            ((Button) pane.lookupButton(ButtonType.CANCEL)).setText("Cancel");


            Optional<ButtonType> result = dialog.showAndWait();
            if (result.isPresent() && result.get() == ButtonType.APPLY) {
                System.out.println("Creating config file: " + confFileName);
                // create base directories, if necessary
                File dir;
                dir = new File(controller.getProjectDir());
                if (! dir.exists()) dir.mkdirs();
                dir = new File(controller.getRawDir());
                if (! dir.exists()) dir.mkdirs();
                dir = new File(controller.getTempDir());
                if (! dir.exists()) dir.mkdirs();

                // TODO: copy parameter files from template directory
                // TODO: create initial config file
                // initialize config directory and config file
                File file = new File(confFileName);

                dir = new File(file.getParent());
                dir.mkdirs();
                file.createNewFile();
                Properties prop = new Properties();
                prop.setProperty("lastProjectDir", controller.getProjectDir());
                prop.setProperty("lastRawDir", controller.getRawDir());
                prop.setProperty("lastTempDir", controller.getTempDir());
                OutputStream outputStream = new FileOutputStream(confFileName);
                prop.store(outputStream, "global settings");
                outputStream.close();
            } else {
                System.exit(1);
            }
        } catch (IOException ex) {
            Logger.getLogger(AirtoolsGUI.class.getName()).log(Level.SEVERE, null, ex);
        }
    }
}
