from llm_sdk.llm_sdk import Small_LLM_Model
import numpy


class StateMachine:
    """Constrain token selection while generating function calls."""

    def __init__(
        self,
        model: Small_LLM_Model,
        functions_json: list[dict],
    ) -> None:
        """Initialize the state machine.

        Args:
            model: Language model used for encoding and decoding tokens.
            functions_json: Function definitions used to constrain outputs.
        """

        self.functions_json: list[dict] = functions_json
        self.model = model
        self.func_ids = self.__get_func_ids()
        self.params_end = False
        self.old_chosen_args: list[str] = []

    def __check_can_chose(
        self, func: str, current_id_idx: int, old_chosen_ids: list[int]
    ) -> bool:
        """Check whether a function prefix remains valid.

        Args:
            func: Function name being evaluated.
            current_id_idx: Current token position in the function name.
            old_chosen_ids: Previously chosen token ids.

        Returns:
            True if the function can still be chosen, otherwise False.
        """

        current_func_ids = self.func_ids[func]

        if len(current_func_ids) <= current_id_idx:
            return False

        for i, old_func_id in enumerate(old_chosen_ids):
            if current_func_ids[i] != old_func_id:
                return False

        return True

    def get_allowed_func_ids(
        self, current_id_idx: int, old_chosen_ids: list[int]
    ) -> tuple[list, list]:
        """Return possible functions and token ids for the next step.

        Args:
            current_id_idx: Current token position in the function name.
            old_chosen_ids: Previously chosen token ids.

        Returns:
            A tuple containing the possible functions and allowed token ids.
        """

        posible_functions = []
        allowed_ids = set()

        for func, ids in self.func_ids.items():

            if not self.__check_can_chose(
                func,
                current_id_idx,
                old_chosen_ids,
            ):
                continue

            posible_functions.append(func)

            allowed_ids.add(ids[current_id_idx])

        return (posible_functions, list(allowed_ids))

    def get_correct_arg(
        self,
        logits: list[float],
        arg_type: str,
    ) -> tuple[int, str]:
        """Select the next argument token and decode its text.

        Args:
            logits: Model logits for the current decoding step.
            arg_type: Expected argument type.

        Returns:
            A tuple of the chosen token id and decoded text.
        """

        max_id = int(numpy.argmax(logits))
        id_decoded = self.model.decode([max_id])
        result = ""

        if arg_type == "number":

            if '"' in id_decoded:
                for c in id_decoded:
                    if c == '"':
                        break
                    result += c
                if "." not in result and "." not in self.old_chosen_args:
                    result += ".0"
                self.old_chosen_args = []
                self.params_end = True
            else:
                self.old_chosen_args.append(id_decoded)
                result = id_decoded

        else:
            if '"' in id_decoded:
                for c in id_decoded:
                    if c == '"':
                        break
                    result += c

                self.old_chosen_args = []
                self.params_end = True
            else:
                result = id_decoded

        return (max_id, result)

    def get_correct_func_id(
        self,
        logits: list[float],
        allowed_ids: list,
    ) -> int:
        """Choose the highest scoring token among the allowed ids.

        Args:
            logits: Model logits for the current decoding step.
            allowed_ids: Token ids that remain valid for the function name.

        Returns:
            The selected token id.
        """

        masked_logits = numpy.full(len(logits), -numpy.inf)

        np_logits = numpy.array(logits)

        masked_logits[allowed_ids] = np_logits[allowed_ids]

        chosen_id = int(numpy.argmax(masked_logits))

        return chosen_id

    def __get_func_ids(self) -> dict[str, list[int]]:
        """Encode all function names into token id sequences.

        Returns:
            A mapping from function name to encoded token ids.
        """

        result: dict[str, list] = {}
        for func in self.functions_json:
            func_name = func["name"]
            func_ids = self.model.encode(func_name).tolist()[0]
            result.setdefault(func_name, []).extend(func_ids)
        return result
