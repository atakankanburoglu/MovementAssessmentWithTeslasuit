using System;
using System.Collections.Generic;
using System.Text;


[Serializable]
public class ModelDataObject
{
    public String subjectIDs; 
    public ExerciseType exerciseType;
    public Algorithm algorithm;
    public String measurmentSets;

    public ModelDataObject(String subjectIDs, ExerciseType exerciseType, Algorithm algorithm, String measurmentSets)
    {
        this.subjectIDs = subjectIDs;
        this.exerciseType = exerciseType;
        this.algorithm = algorithm;
        this.measurmentSets = measurmentSets;
    }

    override
    public String ToString()
    {
        StringBuilder sb = new StringBuilder();
        sb.Append(subjectIDs).Append(";");
        sb.Append(exerciseType).Append(";");
        sb.Append(algorithm).Append(";");
        sb.Append(measurmentSets);
        return sb.ToString();
    }

}
