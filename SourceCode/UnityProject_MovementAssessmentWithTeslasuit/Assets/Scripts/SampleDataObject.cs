using System;
using System.Collections.Generic;
using System.Text;


[Serializable]
public class SampleDataObject
{
    public String subjectID; 
    public ExerciseType exerciseType;
    public SampleType sampleType;

    public SampleDataObject(String subjectID, ExerciseType exerciseType, SampleType sampleType)
    {
        this.subjectID = subjectID;
        this.exerciseType = exerciseType;
        this.sampleType = sampleType;
    }

    override
    public String ToString()
    {
        StringBuilder sb = new StringBuilder();
        sb.Append(subjectID).Append(";");
        sb.Append(exerciseType).Append(";");
        sb.Append(sampleType);
        return sb.ToString();
    }

}
