using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using System;

public class ModeManager : MonoBehaviour
{
    //Sample Setting Panel
    [SerializeField]
    private Dropdown modeDropdown;
    [SerializeField]
    private GameObject trainingUI;
    [SerializeField]
    private GameObject replayUI;
    [SerializeField]
    private GameObject testingUI;

    void Start()
    {
        FillModeDropDown();
    }
   

    void FillModeDropDown()
    {
        string[] names = Enum.GetNames(typeof(ApplicationMode));
        modeDropdown.ClearOptions();
        modeDropdown.AddOptions(new List<string>(names));
    }

    public void OptionChosenFromDropDown()
    {
        ApplicationMode mode = (ApplicationMode)Enum.Parse(typeof(ApplicationMode), modeDropdown.options[modeDropdown.value].text);
        if (mode == ApplicationMode.Testing)
        {
            replayUI.SetActive(false);
            testingUI.SetActive(true);
            trainingUI.SetActive(false);
        }
        else if (mode == ApplicationMode.Replay)
        {
            replayUI.SetActive(true);
            testingUI.SetActive(false);
            trainingUI.SetActive(false);
        }
        else if (mode == ApplicationMode.Training)
        {
            replayUI.SetActive(false);
            testingUI.SetActive(false);
            trainingUI.SetActive(true);
        }
        else
        {
            replayUI.SetActive(false);
            testingUI.SetActive(false);
            trainingUI.SetActive(false);
        }
    }

}
